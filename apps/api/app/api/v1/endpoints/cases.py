from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import get_case_service, get_evidence_service
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.schemas.cases import (
    CaseActionCenterResponse,
    CaseDetail,
    CaseEvidenceClaimLinksResponse,
    CaseInsightsResponse,
    CaseListResponse,
    CaseStatus,
    CaseSummary,
)
from app.services.cases import CaseService
from app.services.evidence import EvidenceService

router = APIRouter()


@router.get("", response_model=CaseListResponse, summary="案件列表")
def list_cases(
    status: CaseStatus | None = Query(default=None, description="案件状态过滤"),
    platform: str | None = Query(default=None, description="平台过滤"),
    limit: int = Query(default=20, ge=1, le=100),
    service: CaseService = Depends(get_case_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseListResponse:
    scope_org = resolve_scope_organization(user)
    items, total = service.list_cases(status=status, platform=platform, organization_id=scope_org, limit=limit)
    return CaseListResponse(total=total, items=items)


@router.get("/insights", response_model=CaseInsightsResponse, summary="案件处置指标")
def get_case_insights(
    service: CaseService = Depends(get_case_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseInsightsResponse:
    return service.get_insights(organization_id=resolve_scope_organization(user))


@router.get("/{case_id}/action-center", response_model=CaseActionCenterResponse, summary="案件动作中心")
def get_case_action_center(
    case_id: str,
    service: CaseService = Depends(get_case_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseActionCenterResponse:
    item = service.get_action_center(case_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return item


@router.get(
    "/{case_id}/evidence-claim-links",
    response_model=CaseEvidenceClaimLinksResponse,
    summary="证据-主张关联",
)
def get_case_evidence_claim_links(
    case_id: str,
    service: CaseService = Depends(get_case_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseEvidenceClaimLinksResponse:
    item = service.get_evidence_claim_links(case_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return item


@router.get("/{case_id}", response_model=CaseDetail, summary="案件详情")
def get_case(
    case_id: str,
    service: CaseService = Depends(get_case_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> CaseDetail:
    item = service.get_case(case_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return item


@router.get("/{case_id}/evidence-packs", summary="案件下证据包列表")
def list_case_evidence_packs(
    case_id: str,
    case_service: CaseService = Depends(get_case_service),
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    scope_org = resolve_scope_organization(user)
    item = case_service.get_case(case_id, organization_id=scope_org)
    if item is None:
        raise HTTPException(status_code=404, detail="案件不存在")
    return evidence_service.list_packs(case_id=case_id, organization_id=scope_org)
