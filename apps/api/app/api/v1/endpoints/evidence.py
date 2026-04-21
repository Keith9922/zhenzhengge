from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from app.api.deps import (
    get_audit_service,
    get_case_service,
    get_evidence_service,
    get_hermes_orchestrator,
    get_playwright_worker,
)
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.schemas.evidence import (
    EvidencePackCreateRequest,
    EvidencePackPreviewResponse,
    EvidencePackRecord,
    EvidencePackResponse,
)
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.playwright import PlaywrightWorker
from app.services.audit import AuditService

router = APIRouter()


@router.get("", summary="证据包列表")
def list_evidence_packs(
    case_id: str | None = None,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> list[EvidencePackRecord]:
    items = evidence_service.list_packs(case_id=case_id, organization_id=resolve_scope_organization(user))
    return items


@router.get("/{evidence_pack_id}", response_model=EvidencePackRecord, summary="证据包详情")
def get_evidence_pack(
    evidence_pack_id: str,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> EvidencePackRecord:
    item = evidence_service.get_pack(evidence_pack_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    return item


@router.get("/{evidence_pack_id}/preview", response_model=EvidencePackPreviewResponse, summary="证据包预览信息")
def get_evidence_pack_preview(
    evidence_pack_id: str,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> EvidencePackPreviewResponse:
    item = evidence_service.get_pack(evidence_pack_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")

    html_content = evidence_service.read_html(item)
    html_excerpt = html_content[:1200]
    screenshot_available = evidence_service.has_screenshot(item)
    html_available = bool(html_content)
    timestamp_available = evidence_service.has_timestamp(item)

    return EvidencePackPreviewResponse(
        item=item,
        screenshot_available=screenshot_available,
        html_available=html_available,
        timestamp_available=timestamp_available,
        screenshot_url=(
            f"/api/v1/evidence-packs/{evidence_pack_id}/artifacts/screenshot" if screenshot_available else None
        ),
        screenshot_download_url=(
            f"/api/v1/evidence-packs/{evidence_pack_id}/artifacts/screenshot?download=1"
            if screenshot_available
            else None
        ),
        html_download_url=(
            f"/api/v1/evidence-packs/{evidence_pack_id}/artifacts/html?download=1" if html_available else None
        ),
        timestamp_download_url=(
            f"/api/v1/evidence-packs/{evidence_pack_id}/artifacts/timestamp?download=1"
            if timestamp_available
            else None
        ),
        html_excerpt=html_excerpt,
    )


@router.get("/{evidence_pack_id}/artifacts/html", response_class=PlainTextResponse, summary="查看或下载 HTML 归档")
def get_evidence_pack_html_artifact(
    evidence_pack_id: str,
    download: bool = False,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    item = evidence_service.get_pack(evidence_pack_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    html_path = evidence_service.resolve_html_path(item)
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="HTML 归档不存在")
    if download:
        return FileResponse(html_path, media_type="text/html; charset=utf-8", filename=f"{evidence_pack_id}.html")
    return PlainTextResponse(html_path.read_text(encoding="utf-8"))


@router.get("/{evidence_pack_id}/artifacts/screenshot", response_class=FileResponse, summary="查看或下载截图归档")
def get_evidence_pack_screenshot_artifact(
    evidence_pack_id: str,
    download: bool = False,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    item = evidence_service.get_pack(evidence_pack_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    screenshot_path = evidence_service.resolve_screenshot_path(item)
    if not screenshot_path.exists() or screenshot_path.stat().st_size == 0:
        raise HTTPException(status_code=404, detail="截图归档不存在")
    filename = f"{evidence_pack_id}.png" if download else screenshot_path.name
    return FileResponse(screenshot_path, media_type="image/png", filename=filename)


@router.get("/{evidence_pack_id}/artifacts/timestamp", response_class=FileResponse, summary="下载可信时间戳回执")
def get_evidence_pack_timestamp_artifact(
    evidence_pack_id: str,
    download: bool = True,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    item = evidence_service.get_pack(evidence_pack_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    if not item.timestamp_token_path:
        raise HTTPException(status_code=404, detail="时间戳回执不存在")
    token_path = evidence_service.resolve_timestamp_path(item)
    if not token_path.exists() or token_path.stat().st_size == 0:
        raise HTTPException(status_code=404, detail="时间戳回执不存在")
    filename = f"{evidence_pack_id}.tsr" if download else token_path.name
    return FileResponse(token_path, media_type="application/timestamp-reply", filename=filename)


@router.post("", response_model=EvidencePackResponse, summary="创建证据包")
def create_evidence_pack(
    payload: EvidencePackCreateRequest,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    case_service: CaseService = Depends(get_case_service),
    hermes: HermesOrchestrator = Depends(get_hermes_orchestrator),
    playwright: PlaywrightWorker = Depends(get_playwright_worker),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> EvidencePackResponse:
    scope_org = resolve_scope_organization(user) or user.organization_id
    capture = playwright.capture(url=str(payload.source_url), title=payload.source_title)
    try:
        record = evidence_service.create_pack(
            payload,
            organization_id=scope_org,
            owner_user_id=user.user_id,
        )
        record = evidence_service.persist_capture_artifacts(
            record,
            raw_html=capture.html_content,
            screenshot_bytes=capture.screenshot_bytes,
            organization_id=scope_org,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    workflow = hermes.submit_capture_workflow(
        payload.case_id,
        case_context={
            "case_id": payload.case_id,
            "title": payload.source_title,
            "platform": "",
            "risk_level": "",
            "description": "",
        },
        evidence_context=[{
            "evidence_pack_id": record.evidence_pack_id,
            "source_url": record.source_url,
            "source_title": record.source_title,
            "chain_sha256": record.chain_sha256,
        }],
    )
    if workflow.status == "completed" and workflow.detail:
        case_service.update_description(payload.case_id, workflow.detail, organization_id=scope_org)
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="evidence_pack.create",
        resource_type="evidence_pack",
        resource_id=record.evidence_pack_id,
        payload={"case_id": payload.case_id, "source_url": str(payload.source_url)},
    )
    return EvidencePackResponse(item=record)
