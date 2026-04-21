from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ApiMessage(BaseModel):
    message: str


class ListEnvelope(BaseModel):
    total: int
    items: list[Any] = Field(default_factory=list)


class ModuleStatus(BaseModel):
    name: str
    status: str
    description: str | None = None


class RuntimeComplianceResponse(BaseModel):
    require_auth: bool
    demo_seed_enabled: bool
    draft_generation_strict: bool
    capture_allow_http_fallback: bool
    harness_agent_enabled: bool
    evidence_timestamp_enabled: bool
    evidence_timestamp_required: bool
    evidence_timestamp_ready: bool
    extension_token_configured: bool
    llm_provider: str
    llm_ready: bool
    compliance_ready: bool
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str
    environment: str
    timestamp: datetime
    uptime_seconds: float
    modules: list[ModuleStatus] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
