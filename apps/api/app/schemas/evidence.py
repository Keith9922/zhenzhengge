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
    organization_id: str = "org-default"
    owner_user_id: str = "system"
    source_url: str
    source_title: str
    capture_channel: str
    note: str | None = None
    hash_sha256: str
    html_sha256: str = ""
    screenshot_sha256: str = ""
    chain_sha256: str = ""
    snapshot_path: str
    html_path: str
    created_at: datetime
    status: str = Field(default="captured")
    timestamp_status: str = Field(default="not_configured")
    timestamp_provider: str = ""
    timestamp_token_path: str = ""
    timestamp_message: str = ""
    timestamp_at: str | None = None


class EvidencePackResponse(BaseModel):
    item: EvidencePackRecord


class EvidencePackPreviewResponse(BaseModel):
    item: EvidencePackRecord
    screenshot_available: bool
    html_available: bool
    timestamp_available: bool = False
    screenshot_url: str | None = None
    screenshot_download_url: str | None = None
    html_download_url: str | None = None
    timestamp_download_url: str | None = None
    html_excerpt: str = ""
