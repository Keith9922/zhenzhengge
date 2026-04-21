from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.api.deps import get_audit_service, get_draft_service
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.schemas.drafts import (
    DocumentDraftCreateRequest,
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
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> DocumentDraftListResponse:
    items = service.list_drafts(case_id=case_id, organization_id=resolve_scope_organization(user))
    return DocumentDraftListResponse(total=len(items), items=items)


@router.post("", response_model=DocumentDraftRecord, summary="生成文书草稿")
def create_draft(
    payload: DocumentDraftCreateRequest,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> DocumentDraftRecord:
    scope_org = resolve_scope_organization(user) or user.organization_id
    try:
        item = service.generate_draft(payload, organization_id=scope_org, owner_user_id=user.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
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
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> DocumentDraftRecord:
    item = service.get_draft(draft_id, organization_id=resolve_scope_organization(user))
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
    scope_org = resolve_scope_organization(user)
    try:
        item = service.update_draft(
            draft_id=draft_id,
            organization_id=scope_org,
            content=payload.content,
            title=payload.title,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
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
    item = service.submit_review(draft_id, payload.comment, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
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
    item = service.approve(draft_id, payload.comment, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
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
    item = service.reject(draft_id, payload.comment, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="draft.reject",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"comment": payload.comment},
    )
    return item


@router.post("/{draft_id}/export", summary="导出草稿为 Word 文件")
def export_draft(
    draft_id: str,
    service: DocumentDraftService = Depends(get_draft_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> FileResponse:
    item = service.export_draft(draft_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    if not item.export_path:
        raise HTTPException(status_code=500, detail="导出失败，文件路径为空")

    base_dir = service.storage.base_dir
    file_path = base_dir / item.export_path
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="导出文件不存在")

    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="draft.export",
        resource_type="document_draft",
        resource_id=draft_id,
        payload={"export_path": item.export_path or ""},
    )
    from urllib.parse import quote
    safe_name = f"{draft_id}.docx"
    display_name = f"{item.title or draft_id}.docx"
    encoded_name = quote(display_name, safe="")
    disposition = f"attachment; filename=\"{safe_name}\"; filename*=UTF-8''{encoded_name}"
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=safe_name,
        headers={"Content-Disposition": disposition},
    )
