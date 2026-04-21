from datetime import datetime

from pydantic import BaseModel, Field


class BrandProfileRecord(BaseModel):
    profile_id: str
    organization_id: str = "org-default"
    owner_user_id: str = "system"
    brand_name: str
    trademark_classes: list[str] = Field(default_factory=list)
    trademark_numbers: list[str] = Field(default_factory=list)
    confusable_terms: list[str] = Field(default_factory=list)
    protection_keywords: list[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class BrandProfileCreateRequest(BaseModel):
    brand_name: str = Field(..., min_length=1)
    trademark_classes: list[str] = Field(default_factory=list)
    trademark_numbers: list[str] = Field(default_factory=list)
    confusable_terms: list[str] = Field(default_factory=list)
    protection_keywords: list[str] = Field(default_factory=list)


class BrandProfileUpdateRequest(BaseModel):
    brand_name: str | None = None
    trademark_classes: list[str] | None = None
    trademark_numbers: list[str] | None = None
    confusable_terms: list[str] | None = None
    protection_keywords: list[str] | None = None


class BrandProfileListResponse(BaseModel):
    total: int
    items: list[BrandProfileRecord]


class SuggestConfusableResponse(BaseModel):
    brand_name: str
    suggestions: list[str]
