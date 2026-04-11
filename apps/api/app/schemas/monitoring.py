from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, HttpUrl


class MonitorTaskStatus(str, Enum):
    active = "active"
    paused = "paused"


class MonitorTaskRecord(BaseModel):
    task_id: str
    name: str
    target_url: str
    target_type: str
    site: str
    brand_keywords: list[str] = Field(default_factory=list)
    frequency_minutes: int = Field(ge=5, le=10080)
    risk_threshold: int = Field(ge=0, le=100)
    status: MonitorTaskStatus
    created_at: datetime
    updated_at: datetime
    last_run_at: datetime | None = None


class MonitorTaskCreateRequest(BaseModel):
    name: str
    target_url: HttpUrl
    target_type: str = "page"
    site: str
    brand_keywords: list[str] = Field(default_factory=list)
    frequency_minutes: int = Field(default=60, ge=5, le=10080)
    risk_threshold: int = Field(default=70, ge=0, le=100)


class MonitorTaskToggleRequest(BaseModel):
    enabled: bool


class MonitorTaskListResponse(BaseModel):
    total: int
    items: list[MonitorTaskRecord]
