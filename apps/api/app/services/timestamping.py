from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import httpx

from app.core.config import Settings


@dataclass(slots=True)
class TimestampIssueResult:
    status: str
    provider: str
    token_bytes: bytes
    message: str
    issued_at: str | None = None


class TrustedTimestampService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return bool(self.settings.evidence_timestamp_enabled)

    @property
    def provider_url(self) -> str:
        return self.settings.evidence_timestamp_tsa_url.strip()

    def health(self) -> dict[str, str]:
        if not self.enabled:
            return {
                "name": "trusted_timestamp",
                "status": "disabled",
                "description": "可信时间戳未启用（ZHZG_EVIDENCE_TIMESTAMP_ENABLED=false）",
            }
        if not self.provider_url:
            return {
                "name": "trusted_timestamp",
                "status": "degraded",
                "description": "可信时间戳已启用，但未配置 TSA 地址（ZHZG_EVIDENCE_TIMESTAMP_TSA_URL）",
            }
        if shutil.which("openssl") is None:
            return {
                "name": "trusted_timestamp",
                "status": "degraded",
                "description": "系统未安装 openssl，无法发起 RFC3161 时间戳请求",
            }
        return {
            "name": "trusted_timestamp",
            "status": "ready",
            "description": f"可信时间戳可用，TSA={self.provider_url}",
        }

    def issue_timestamp(self, payload: bytes) -> TimestampIssueResult:
        if not self.enabled:
            return TimestampIssueResult(
                status="disabled",
                provider=self.provider_url,
                token_bytes=b"",
                message="可信时间戳未启用",
            )
        if not self.provider_url:
            return TimestampIssueResult(
                status="failed",
                provider="",
                token_bytes=b"",
                message="未配置 TSA 地址",
            )
        if shutil.which("openssl") is None:
            return TimestampIssueResult(
                status="failed",
                provider=self.provider_url,
                token_bytes=b"",
                message="未安装 openssl，无法生成 RFC3161 请求",
            )

        try:
            with tempfile.TemporaryDirectory(prefix="zhzg-ts-") as tmp:
                temp_dir = Path(tmp)
                data_path = str(temp_dir / "payload.bin")
                req_path = str(temp_dir / "request.tsq")
                tsr_path = str(temp_dir / "response.tsr")

                with open(data_path, "wb") as data_file:
                    data_file.write(payload)

                query = subprocess.run(
                    ["openssl", "ts", "-query", "-data", data_path, "-sha256", "-cert", "-out", req_path],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if query.returncode != 0:
                    stderr = (query.stderr or "").strip()
                    return TimestampIssueResult(
                        status="failed",
                        provider=self.provider_url,
                        token_bytes=b"",
                        message=f"生成时间戳请求失败：{stderr}",
                    )

                with open(req_path, "rb") as request_file:
                    request_bytes = request_file.read()

                response = httpx.post(
                    self.provider_url,
                    content=request_bytes,
                    headers={"Content-Type": "application/timestamp-query"},
                    timeout=max(5, int(self.settings.evidence_timestamp_timeout_seconds)),
                )
                response.raise_for_status()
                token_bytes = response.content
                if not token_bytes:
                    return TimestampIssueResult(
                        status="failed",
                        provider=self.provider_url,
                        token_bytes=b"",
                        message="TSA 返回空响应",
                    )

                with open(tsr_path, "wb") as tsr_file:
                    tsr_file.write(token_bytes)

                text_reply = subprocess.run(
                    ["openssl", "ts", "-reply", "-in", tsr_path, "-text"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                issued_at = self._parse_issued_at(text_reply.stdout if text_reply.returncode == 0 else "")
                return TimestampIssueResult(
                    status="ok",
                    provider=self.provider_url,
                    token_bytes=token_bytes,
                    message="可信时间戳签发成功",
                    issued_at=issued_at,
                )
        except Exception as exc:
            return TimestampIssueResult(
                status="failed",
                provider=self.provider_url,
                token_bytes=b"",
                message=f"时间戳请求异常：{exc}",
            )

    @staticmethod
    def _parse_issued_at(raw_text: str) -> str | None:
        if not raw_text:
            return None
        match = re.search(r"Time stamp:\s*(.+)", raw_text)
        if not match:
            return None
        value = match.group(1).strip()
        for pattern in ("%b %d %H:%M:%S %Y GMT", "%Y-%m-%d %H:%M:%S"):
            try:
                parsed = datetime.strptime(value, pattern)
                return parsed.isoformat() + ("Z" if "GMT" in pattern else "")
            except ValueError:
                continue
        return value
