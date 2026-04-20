from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_case_service, get_evidence_service
from app.api.security import CurrentUser, require_roles
from app.schemas.cases import CaseDetail, CaseListResponse, CaseStatus, CaseSummary
from app.services.cases import CaseService
from app.services.evidence import EvidenceService

router = APIRouter()


@router.get("", response_model=CaseListResponse, summary="案件列表")
def list_cases(
    status: CaseStatus | None = Query(default=None, description="案件状态过滤"),
    platform: str | None = Query(default=None, description="平台过滤"),
    limit: int = Query(default=20, ge=1, le=100),
    service: CaseService = Depends(get_case_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseListResponse:
    items, total = service.list_cases(status=status, platform=platform, limit=limit)
    return CaseListResponse(total=total, items=items)


@router.get("/{case_id}", response_model=CaseDetail, summary="案件详情")
def get_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseDetail:
    item = service.get_case(case_id)
    if item is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return item


@router.get("/{case_id}/evidence-packs", summary="案件下证据包列表")
def list_case_evidence_packs(
    case_id: str,
    case_service: CaseService = Depends(get_case_service),
    evidence_service: EvidenceService = Depends(get_evidence_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    item = case_service.get_case(case_id)
    if item is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return evidence_service.list_packs(case_id=case_id)
