from app.core.storage import SQLiteStorage
from app.schemas.cases import CaseCreateRequest, CaseDetail, CaseStatus, CaseSummary


class CaseService:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def create_case(self, payload: CaseCreateRequest) -> CaseDetail:
        return self.storage.create_case(payload)

    def attach_evidence(self, case_id: str) -> CaseDetail | None:
        return self.storage.attach_evidence(case_id)

    def list_cases(
        self,
        *,
        status: CaseStatus | None = None,
        platform: str | None = None,
        limit: int = 20,
    ) -> tuple[list[CaseSummary], int]:
        return self.storage.list_cases(status=status, platform=platform, limit=limit)

    def get_case(self, case_id: str) -> CaseDetail | None:
        return self.storage.get_case(case_id)
