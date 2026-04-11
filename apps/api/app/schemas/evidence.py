from datetime import datetime

from pydantic import BaseModel, HttpUrl, Field


class EvidencePackCreateRequest(BaseModel):
    case_id: str
    source_url: HttpUrl
    source_title: str
    capture_channel: str = "browser_extension"
    note: str | None = None


class EvidencePackRecord(BaseModel):
    evidence_pack_id: str
    case_id: str
    source_url: str
    source_title: str
    capture_channel: str
    note: str | None = None
    hash_sha256: str
    snapshot_path: str
    html_path: str
    created_at: datetime
    status: str = Field(default="captured")


class EvidencePackResponse(BaseModel):
    item: EvidencePackRecord

