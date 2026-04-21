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
    organization_id: str = "org-default"
    owner_user_id: str = "system"
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


class CaseCreateRequest(BaseModel):
    title: str
    brand_name: str
    suspect_name: str
    platform: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    description: str
    tags: list[str] = Field(default_factory=list)
    monitoring_scope: list[str] = Field(default_factory=list)


class CaseListResponse(BaseModel):
    total: int
    items: list[CaseSummary]


class CaseActionItem(BaseModel):
    action_id: str
    title: str
    description: str
    priority: str
    cta_label: str
    href: str


class CaseActionCenterResponse(BaseModel):
    case_id: str
    generated_at: datetime
    items: list[CaseActionItem]


class EvidenceClaimReference(BaseModel):
    draft_id: str
    draft_title: str
    line_no: int
    claim_text: str


class CaseEvidenceClaimLinkItem(BaseModel):
    evidence_pack_id: str
    source_title: str
    claim_count: int
    claims: list[EvidenceClaimReference]


class CaseEvidenceClaimLinksResponse(BaseModel):
    case_id: str
    generated_at: datetime
    total_evidence: int
    total_claims: int
    items: list[CaseEvidenceClaimLinkItem]


class CaseInsightsResponse(BaseModel):
    generated_at: datetime
    total_cases: int
    cases_with_actions: int
    action_rate: float
    evidence_pass_rate: float
    tta_hours: float | None = None
