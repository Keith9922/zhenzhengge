from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DraftStatus(str, Enum):
    generated = "generated"
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    exported = "exported"


class DocumentDraftRecord(BaseModel):
    draft_id: str
    case_id: str
    template_key: str
    title: str
    status: DraftStatus
    content: str
    created_at: datetime
    updated_at: datetime
    review_comment: str | None = None
    export_path: str | None = None


class DocumentDraftCreateRequest(BaseModel):
    case_id: str
    template_key: str
    variables_override: dict[str, str] = Field(default_factory=dict)


class DocumentDraftReviewRequest(BaseModel):
    comment: str = ""


class DocumentDraftExportResponse(BaseModel):
    item: DocumentDraftRecord
    file_path: str | None = None


class DocumentDraftListResponse(BaseModel):
    total: int
    items: list[DocumentDraftRecord]
