from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_audit_service, get_draft_service
from app.api.security import CurrentUser, require_roles
from app.schemas.drafts import (
    DocumentDraftCreateRequest,
    DocumentDraftExportResponse,
    DocumentDraftListResponse,
    DocumentDraftReviewRequest,
    DocumentDraftRecord,
    DocumentDraftUpdateRequest,
)
from app.services.audit import AuditService
from app.services.drafts import DocumentDraftService

router = APIRouter()


@router.get("", response_model=DocumentDraftListResponse, summary="文书草稿列表")
def list_drafts(
    case_id: str | None = None,
    service: DocumentDraftService = Depends(get_draft_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> DocumentDraftListResponse:
    items = service.list_drafts(case_id=case_id)
    return DocumentDraftListResponse(total=len(items), items=items)


@router.post("", response_model=DocumentDraftRecord, summary="生成文书草稿")
def create_draft(
    payload: DocumentDraftCreateRequest,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftRecord:
    try:
        item = service.generate_draft(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="draft.create",
        resource_type="document_draft",
        resource_id=item.draft_id,
        payload={"case_id": payload.case_id, "template_key": payload.template_key},
    )
    return item


@router.get("/{draft_id}", response_model=DocumentDraftRecord, summary="草稿详情")
def get_draft(
    draft_id: str,
    service: DocumentDraftService = Depends(get_draft_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> DocumentDraftRecord:
    item = service.get_draft(draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    return item


@router.patch("/{draft_id}", response_model=DocumentDraftRecord, summary="更新草稿内容")
def update_draft(
    draft_id: str,
    payload: DocumentDraftUpdateRequest,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftRecord:
    try:
        item = service.update_draft(draft_id=draft_id, content=payload.content, title=payload.title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="draft.update",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"title": payload.title or "", "content_length": len(payload.content)},
    )
    return item


@router.post("/{draft_id}/submit-review", response_model=DocumentDraftRecord, summary="提交审核")
def submit_review(
    draft_id: str,
    payload: DocumentDraftReviewRequest,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftRecord:
    item = service.submit_review(draft_id, payload.comment)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="draft.submit_review",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"comment": payload.comment},
    )
    return item


@router.post("/{draft_id}/approve", response_model=DocumentDraftRecord, summary="通过审核")
def approve_draft(
    draft_id: str,
    payload: DocumentDraftReviewRequest,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftRecord:
    item = service.approve(draft_id, payload.comment)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="draft.approve",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"comment": payload.comment},
    )
    return item


@router.post("/{draft_id}/reject", response_model=DocumentDraftRecord, summary="驳回审核")
def reject_draft(
    draft_id: str,
    payload: DocumentDraftReviewRequest,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftRecord:
    item = service.reject(draft_id, payload.comment)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="draft.reject",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"comment": payload.comment},
    )
    return item


@router.post("/{draft_id}/export", response_model=DocumentDraftExportResponse, summary="导出草稿")
def export_draft(
    draft_id: str,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftExportResponse:
    item = service.export_draft(draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="draft.export",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"export_path": item.export_path or ""},
    )
    return DocumentDraftExportResponse(item=item, file_path=item.export_path)
