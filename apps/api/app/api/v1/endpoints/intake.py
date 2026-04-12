from fastapi import APIRouter, Depends

from app.api.deps import get_intake_service
from app.schemas.intake import EvidenceIntakeRequest, EvidenceIntakeResponse
from app.services.intake import IntakeService

router = APIRouter()


@router.post("/intake", response_model=EvidenceIntakeResponse, summary="插件 intake")
def plugin_intake(
    payload: EvidenceIntakeRequest,
    service: IntakeService = Depends(get_intake_service),
) -> EvidenceIntakeResponse:
    case, evidence_pack, generated_draft = service.intake(payload)
    return EvidenceIntakeResponse(
        case=case,
        evidence_pack=evidence_pack,
        generated_draft=generated_draft,
    )
