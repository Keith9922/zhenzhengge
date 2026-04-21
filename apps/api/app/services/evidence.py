import base64
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

from app.core.config import Settings, settings as global_settings
from app.core.storage import SQLiteStorage
from app.schemas.evidence import EvidencePackCreateRequest, EvidencePackRecord
from app.services.timestamping import TrustedTimestampService


class EvidenceService:
    def __init__(self, storage: SQLiteStorage, *, settings: Settings | None = None) -> None:
        self.storage = storage
        self.settings = settings or global_settings
        self.timestamp_service = TrustedTimestampService(self.settings)

    def timestamp_health(self) -> dict[str, str]:
        return self.timestamp_service.health()

    def create_pack(
        self,
        payload: EvidencePackCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> EvidencePackRecord:
        case = self.storage.get_case(payload.case_id, organization_id=organization_id)
        if case is None:
            raise ValueError("案件不存在或无权限")
        return self.storage.create_evidence_pack(payload, organization_id=organization_id, owner_user_id=owner_user_id)

    def create_pack_for_case(
        self,
        *,
        case_id: str,
        organization_id: str,
        owner_user_id: str,
        source_url: str,
        source_title: str,
        note: str | None = None,
        capture_channel: str = "browser_extension",
    ) -> EvidencePackRecord:
        payload = EvidencePackCreateRequest(
            case_id=case_id,
            source_url=source_url,
            source_title=source_title,
            capture_channel=capture_channel,
            note=note,
        )
        return self.create_pack(payload, organization_id=organization_id, owner_user_id=owner_user_id)

    def list_packs(
        self,
        case_id: str | None = None,
        *,
        organization_id: str | None = None,
    ) -> list[EvidencePackRecord]:
        return self.storage.list_evidence_packs(case_id=case_id, organization_id=organization_id)

    def get_pack(self, evidence_pack_id: str, *, organization_id: str | None = None) -> EvidencePackRecord | None:
        return self.storage.get_evidence_pack(evidence_pack_id, organization_id=organization_id)

    def persist_capture_artifacts(
        self,
        record: EvidencePackRecord,
        *,
        raw_html: str = "",
        screenshot_base64: str = "",
        screenshot_bytes: bytes | None = None,
        organization_id: str | None = None,
    ) -> EvidencePackRecord:
        base_dir = self.storage.base_dir
        html_path = base_dir / record.html_path
        screenshot_path = base_dir / record.snapshot_path

        html_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)

        html_payload = raw_html or ""
        html_path.write_text(html_payload, encoding="utf-8")

        if screenshot_bytes:
            screenshot_path.write_bytes(screenshot_bytes)
        elif screenshot_base64:
            payload = screenshot_base64.split(",", 1)[-1]
            try:
                screenshot_path.write_bytes(base64.b64decode(payload))
            except Exception:
                screenshot_path.write_bytes(b"")
        elif not screenshot_path.exists():
            screenshot_path.write_bytes(b"")

        html_sha = sha256(html_path.read_bytes()).hexdigest()
        screenshot_sha = sha256(screenshot_path.read_bytes()).hexdigest()
        chain_sha = sha256(f"{record.hash_sha256}:{html_sha}:{screenshot_sha}".encode("utf-8")).hexdigest()
        updated = self.storage.update_evidence_hashes(
            evidence_pack_id=record.evidence_pack_id,
            organization_id=organization_id or record.organization_id,
            hash_sha256=chain_sha,
            html_sha256=html_sha,
            screenshot_sha256=screenshot_sha,
            chain_sha256=chain_sha,
        )
        current = updated or record
        timestamp_result = self._issue_timestamp(
            current,
            payload=json.dumps(
                {
                    "evidence_pack_id": current.evidence_pack_id,
                    "case_id": current.case_id,
                    "hash_sha256": current.hash_sha256,
                    "html_sha256": current.html_sha256,
                    "screenshot_sha256": current.screenshot_sha256,
                    "chain_sha256": current.chain_sha256,
                    "captured_at": current.created_at.isoformat(),
                },
                ensure_ascii=False,
            ).encode("utf-8"),
        )
        return timestamp_result

    def resolve_html_path(self, record: EvidencePackRecord) -> Path:
        return self.storage.base_dir / record.html_path

    def resolve_screenshot_path(self, record: EvidencePackRecord) -> Path:
        return self.storage.base_dir / record.snapshot_path

    def resolve_timestamp_path(self, record: EvidencePackRecord) -> Path:
        return self.storage.base_dir / record.timestamp_token_path

    def read_html(self, record: EvidencePackRecord) -> str:
        path = self.resolve_html_path(record)
        if not path.exists():
            return ""
        return path.read_text(encoding="utf-8")

    def has_html(self, record: EvidencePackRecord) -> bool:
        return self.resolve_html_path(record).exists()

    def has_screenshot(self, record: EvidencePackRecord) -> bool:
        path = self.resolve_screenshot_path(record)
        return path.exists() and path.stat().st_size > 0

    def has_timestamp(self, record: EvidencePackRecord) -> bool:
        if not record.timestamp_token_path:
            return False
        path = self.resolve_timestamp_path(record)
        return path.exists() and path.stat().st_size > 0

    def _issue_timestamp(self, record: EvidencePackRecord, *, payload: bytes) -> EvidencePackRecord:
        result = self.timestamp_service.issue_timestamp(payload)
        token_path = ""
        issued_at: str | None = None
        if result.status == "ok":
            ts_dir = self.storage.base_dir / "evidence" / record.case_id
            ts_dir.mkdir(parents=True, exist_ok=True)
            path = ts_dir / f"timestamp-{record.evidence_pack_id}.tsr"
            path.write_bytes(result.token_bytes)
            token_path = path.relative_to(self.storage.base_dir).as_posix()
            status = "stamped"
            message = "可信时间戳签发成功"
            issued_at = result.issued_at
        else:
            # TSA 不可用时降级为本地哈希链存证
            status = "hash_only"
            message = "本地 SHA-256 哈希链存证"
            issued_at = datetime.now(timezone.utc).isoformat()
        updated = self.storage.update_evidence_timestamp(
            evidence_pack_id=record.evidence_pack_id,
            organization_id=record.organization_id,
            timestamp_status=status,
            timestamp_provider="local-sha256" if status == "hash_only" else result.provider,
            timestamp_token_path=token_path,
            timestamp_message=message,
            timestamp_at=issued_at,
        )
        return updated or record
