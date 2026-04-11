from app.schemas.cases import CaseDetail, CaseCreateRequest
from app.schemas.evidence import EvidencePackRecord
from app.schemas.intake import EvidenceIntakeRequest
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.playwright import PlaywrightWorker


class IntakeService:
    def __init__(
        self,
        *,
        case_service: CaseService,
        evidence_service: EvidenceService,
        hermes: HermesOrchestrator,
        playwright: PlaywrightWorker,
    ) -> None:
        self.case_service = case_service
        self.evidence_service = evidence_service
        self.hermes = hermes
        self.playwright = playwright

    def intake(self, payload: EvidenceIntakeRequest) -> tuple[CaseDetail, EvidencePackRecord]:
        case = self.case_service.create_case(
            CaseCreateRequest(
                title=payload.title,
                brand_name=payload.brand_name,
                suspect_name=payload.suspect_name,
                platform=payload.platform,
                risk_score=88,
                risk_level="high",
                description=payload.description,
                tags=payload.tags,
                monitoring_scope=payload.monitoring_scope,
            )
        )
        _ = self.hermes.submit_capture_workflow(case.case_id)
        _ = self.playwright.capture(url=str(payload.source_url), title=payload.source_title)
        evidence = self.evidence_service.create_pack_for_case(
            case_id=case.case_id,
            source_url=str(payload.source_url),
            source_title=payload.source_title,
            note=payload.note,
        )
        self.case_service.attach_evidence(case.case_id)
        return case, evidence
