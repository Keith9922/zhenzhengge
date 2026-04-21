from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class NotificationChannelType(str, Enum):
    email = "email"
    dingtalk = "dingtalk"


class NotificationChannelRecord(BaseModel):
    channel_id: str
    organization_id: str = "org-default"
    owner_user_id: str = "system"
    channel_type: NotificationChannelType
    name: str
    target: str
    enabled: bool
    created_at: datetime
    updated_at: datetime


class NotificationChannelCreateRequest(BaseModel):
    channel_type: NotificationChannelType
    name: str
    target: str
    enabled: bool = True


class NotificationChannelTestRequest(BaseModel):
    subject: str
    body: str


class NotificationChannelListResponse(BaseModel):
    total: int
    items: list[NotificationChannelRecord]
