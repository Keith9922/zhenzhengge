from fastapi import APIRouter, Depends
from fastapi import HTTPException

from app.api.deps import get_evidence_service, get_hermes_orchestrator, get_playwright_worker
from app.schemas.evidence import EvidencePackCreateRequest, EvidencePackRecord, EvidencePackResponse
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.playwright import PlaywrightWorker

router = APIRouter()


@router.get("", summary="证据包列表")
def list_evidence_packs(
    case_id: str | None = None,
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> list[EvidencePackRecord]:
    items = evidence_service.list_packs(case_id=case_id)
    return items


@router.get("/{evidence_pack_id}", response_model=EvidencePackRecord, summary="证据包详情")
def get_evidence_pack(
    evidence_pack_id: str,
    evidence_service: EvidenceService = Depends(get_evidence_service),
) -> EvidencePackRecord:
    item = evidence_service.get_pack(evidence_pack_id)
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    return item


@router.post("", response_model=EvidencePackResponse, summary="创建证据包")
def create_evidence_pack(
    payload: EvidencePackCreateRequest,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    hermes: HermesOrchestrator = Depends(get_hermes_orchestrator),
    playwright: PlaywrightWorker = Depends(get_playwright_worker),
) -> EvidencePackResponse:
    # 这里先做最小闭环：记录证据包，后续由 Hermes / Playwright 承接真实抓取。
    _ = hermes.submit_capture_workflow(payload.case_id)
    _ = playwright.capture(url=str(payload.source_url), title=payload.source_title)
    record = evidence_service.create_pack(payload)
    return EvidencePackResponse(item=record)
