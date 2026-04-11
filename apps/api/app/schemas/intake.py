from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.schemas.cases import CaseDetail
from app.schemas.evidence import EvidencePackRecord


class EvidenceIntakeRequest(BaseModel):
    url: HttpUrl
    title: str
    captured_at: datetime = Field(alias="capturedAt")
    source: str | None = None
    page_text: str = Field(default="", alias="pageText")
    html: str = ""
    screenshot_base64: str = Field(default="", alias="screenshotBase64")
    request_id: str = Field(alias="requestId")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


class EvidenceIntakeResponse(BaseModel):
    case: CaseDetail
    evidence_pack: EvidencePackRecord
