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


class HealthResponse(BaseModel):
    service: str
    status: str
    version: str
    environment: str
    timestamp: datetime
    uptime_seconds: float
    modules: list[ModuleStatus] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

