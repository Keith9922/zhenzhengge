from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    open = "open"
    monitoring = "monitoring"
    triaged = "triaged"
    drafting = "drafting"
    review = "review"
    archived = "archived"


class CaseSummary(BaseModel):
    case_id: str
    title: str
    brand_name: str
    suspect_name: str
    platform: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    status: CaseStatus
    updated_at: datetime


class CaseDetail(CaseSummary):
    description: str
    evidence_count: int = 0
    template_count: int = 0
    tags: list[str] = Field(default_factory=list)
    monitoring_scope: list[str] = Field(default_factory=list)


class CaseListResponse(BaseModel):
    total: int
    items: list[CaseSummary]

