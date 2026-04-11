from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_draft_service
from app.schemas.drafts import (
    DocumentDraftCreateRequest,
    DocumentDraftExportResponse,
    DocumentDraftListResponse,
    DocumentDraftReviewRequest,
    DocumentDraftRecord,
)
from app.services.drafts import DocumentDraftService

router = APIRouter()


@router.get("", response_model=DocumentDraftListResponse, summary="文书草稿列表")
def list_drafts(
    case_id: str | None = None,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftListResponse:
    items = service.list_drafts(case_id=case_id)
    return DocumentDraftListResponse(total=len(items), items=items)


@router.post("", response_model=DocumentDraftRecord, summary="生成文书草稿")
def create_draft(
    payload: DocumentDraftCreateRequest,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftRecord:
    try:
        return service.generate_draft(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{draft_id}", response_model=DocumentDraftRecord, summary="草稿详情")
def get_draft(
    draft_id: str,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftRecord:
    item = service.get_draft(draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    return item


@router.post("/{draft_id}/submit-review", response_model=DocumentDraftRecord, summary="提交审核")
def submit_review(
    draft_id: str,
    payload: DocumentDraftReviewRequest,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftRecord:
    item = service.submit_review(draft_id, payload.comment)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    return item


@router.post("/{draft_id}/approve", response_model=DocumentDraftRecord, summary="通过审核")
def approve_draft(
    draft_id: str,
    payload: DocumentDraftReviewRequest,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftRecord:
    item = service.approve(draft_id, payload.comment)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    return item


@router.post("/{draft_id}/reject", response_model=DocumentDraftRecord, summary="驳回审核")
def reject_draft(
    draft_id: str,
    payload: DocumentDraftReviewRequest,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftRecord:
    item = service.reject(draft_id, payload.comment)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    return item


@router.post("/{draft_id}/export", response_model=DocumentDraftExportResponse, summary="导出草稿")
def export_draft(
    draft_id: str,
    service: DocumentDraftService = Depends(get_draft_service),
) -> DocumentDraftExportResponse:
    item = service.export_draft(draft_id)
    if item is None:
        raise HTTPException(status_code=404, detail="草稿不存在")
    return DocumentDraftExportResponse(item=item, file_path=item.export_path)
