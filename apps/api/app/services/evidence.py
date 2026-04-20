import base64
from hashlib import sha256
from pathlib import Path

from app.core.storage import SQLiteStorage
from app.schemas.evidence import EvidencePackCreateRequest, EvidencePackRecord


class EvidenceService:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def create_pack(self, payload: EvidencePackCreateRequest) -> EvidencePackRecord:
        return self.storage.create_evidence_pack(payload)

    def create_pack_for_case(
        self,
        *,
        case_id: str,
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
        return self.create_pack(payload)

    def list_packs(self, case_id: str | None = None) -> list[EvidencePackRecord]:
        return self.storage.list_evidence_packs(case_id=case_id)

    def get_pack(self, evidence_pack_id: str) -> EvidencePackRecord | None:
        return self.storage.get_evidence_pack(evidence_pack_id)

    def persist_capture_artifacts(
        self,
        record: EvidencePackRecord,
        *,
        raw_html: str = "",
        screenshot_base64: str = "",
        screenshot_bytes: bytes | None = None,
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
            hash_sha256=chain_sha,
            html_sha256=html_sha,
            screenshot_sha256=screenshot_sha,
            chain_sha256=chain_sha,
        )
        return updated or record

    def resolve_html_path(self, record: EvidencePackRecord) -> Path:
        return self.storage.base_dir / record.html_path

    def resolve_screenshot_path(self, record: EvidencePackRecord) -> Path:
        return self.storage.base_dir / record.snapshot_path

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
