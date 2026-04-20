from fastapi import APIRouter, Depends
from fastapi import HTTPException
from fastapi.responses import FileResponse, PlainTextResponse

from app.api.deps import (
    get_audit_service,
    get_evidence_service,
    get_hermes_orchestrator,
    get_playwright_worker,
)
from app.api.security import CurrentUser, require_roles
from app.schemas.evidence import (
    EvidencePackCreateRequest,
    EvidencePackPreviewResponse,
    EvidencePackRecord,
    EvidencePackResponse,
)
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.playwright import PlaywrightWorker
from app.services.audit import AuditService

router = APIRouter()


@router.get("", summary="证据包列表")
def list_evidence_packs(
    case_id: str | None = None,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> list[EvidencePackRecord]:
    items = evidence_service.list_packs(case_id=case_id)
    return items


@router.get("/{evidence_pack_id}", response_model=EvidencePackRecord, summary="证据包详情")
def get_evidence_pack(
    evidence_pack_id: str,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> EvidencePackRecord:
    item = evidence_service.get_pack(evidence_pack_id)
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    return item


@router.get("/{evidence_pack_id}/preview", response_model=EvidencePackPreviewResponse, summary="证据包预览信息")
def get_evidence_pack_preview(
    evidence_pack_id: str,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> EvidencePackPreviewResponse:
    item = evidence_service.get_pack(evidence_pack_id)
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")

    html_content = evidence_service.read_html(item)
    html_excerpt = html_content[:1200]
    screenshot_available = evidence_service.has_screenshot(item)
    html_available = bool(html_content)

    return EvidencePackPreviewResponse(
        item=item,
        screenshot_available=screenshot_available,
        html_available=html_available,
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
        html_excerpt=html_excerpt,
    )


@router.get("/{evidence_pack_id}/artifacts/html", response_class=PlainTextResponse, summary="查看或下载 HTML 归档")
def get_evidence_pack_html_artifact(
    evidence_pack_id: str,
    download: bool = False,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    item = evidence_service.get_pack(evidence_pack_id)
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
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
):
    item = evidence_service.get_pack(evidence_pack_id)
    if item is None:
        raise HTTPException(status_code=404, detail="证据包不存在")
    screenshot_path = evidence_service.resolve_screenshot_path(item)
    if not screenshot_path.exists() or screenshot_path.stat().st_size == 0:
        raise HTTPException(status_code=404, detail="截图归档不存在")
    filename = f"{evidence_pack_id}.png" if download else screenshot_path.name
    return FileResponse(screenshot_path, media_type="image/png", filename=filename)


@router.post("", response_model=EvidencePackResponse, summary="创建证据包")
def create_evidence_pack(
    payload: EvidencePackCreateRequest,
    evidence_service: EvidenceService = Depends(get_evidence_service),
    hermes: HermesOrchestrator = Depends(get_hermes_orchestrator),
    playwright: PlaywrightWorker = Depends(get_playwright_worker),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> EvidencePackResponse:
    _ = hermes.submit_capture_workflow(payload.case_id)
    capture = playwright.capture(url=str(payload.source_url), title=payload.source_title)
    record = evidence_service.create_pack(payload)
    record = evidence_service.persist_capture_artifacts(
        record,
        raw_html=capture.html_content,
        screenshot_bytes=capture.screenshot_bytes,
    )
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="evidence_pack.create",
        resource_type="evidence_pack",
        resource_id=record.evidence_pack_id,
        payload={"case_id": payload.case_id, "source_url": str(payload.source_url)},
    )
    return EvidencePackResponse(item=record)
