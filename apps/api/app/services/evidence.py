import base64
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
    ) -> EvidencePackRecord:
        base_dir = Path(self.storage.db_path).resolve().parent if self.storage.db_path != ":memory:" else Path.cwd()
        html_path = base_dir / record.html_path
        screenshot_path = base_dir / record.snapshot_path

        html_path.parent.mkdir(parents=True, exist_ok=True)
        screenshot_path.parent.mkdir(parents=True, exist_ok=True)

        html_path.write_text(raw_html or "<html><body>capture placeholder</body></html>", encoding="utf-8")

        if screenshot_base64:
            payload = screenshot_base64.split(",", 1)[-1]
            try:
                screenshot_path.write_bytes(base64.b64decode(payload))
            except Exception:
                screenshot_path.write_bytes(b"")
        elif not screenshot_path.exists():
            screenshot_path.write_bytes(b"")

        return record
