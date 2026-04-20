from datetime import datetime

from pydantic import BaseModel, HttpUrl, Field


class EvidencePackCreateRequest(BaseModel):
    case_id: str
    source_url: HttpUrl
    source_title: str
    capture_channel: str = "browser_extension"
    note: str | None = None


class EvidencePackCreateByIntakeRequest(BaseModel):
    title: str
    brand_name: str
    suspect_name: str
    platform: str
    source_url: HttpUrl
    source_title: str
    description: str = ""
    note: str | None = None
    monitoring_scope: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class EvidencePackRecord(BaseModel):
    evidence_pack_id: str
    case_id: str
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


class EvidencePackResponse(BaseModel):
    item: EvidencePackRecord


class EvidencePackPreviewResponse(BaseModel):
    item: EvidencePackRecord
    screenshot_available: bool
    html_available: bool
    screenshot_url: str | None = None
    screenshot_download_url: str | None = None
    html_download_url: str | None = None
    html_excerpt: str = ""
