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
