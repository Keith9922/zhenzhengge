from pydantic import BaseModel, Field, HttpUrl

from app.schemas.cases import CaseDetail
from app.schemas.evidence import EvidencePackRecord


class EvidenceIntakeRequest(BaseModel):
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


class EvidenceIntakeResponse(BaseModel):
    case: CaseDetail
    evidence_pack: EvidencePackRecord
