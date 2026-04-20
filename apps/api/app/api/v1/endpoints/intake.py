from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_audit_service, get_intake_service
from app.api.security import CurrentUser, require_roles
from app.schemas.intake import EvidenceIntakeRequest, EvidenceIntakeResponse
from app.services.audit import AuditService
from app.services.intake import IntakeService

router = APIRouter()


@router.post("/intake", response_model=EvidenceIntakeResponse, summary="插件 intake")
def plugin_intake(
    payload: EvidenceIntakeRequest,
    service: IntakeService = Depends(get_intake_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> EvidenceIntakeResponse:
    try:
        case, evidence_pack, generated_draft = service.intake(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"取证处理失败：{exc}") from exc
    audit.log(
        actor_token=user.token,
        actor_role=user.role,
        action="intake.submit",
        resource_type="case",
        resource_id=case.case_id,
        payload={
            "request_id": payload.request_id,
            "source_url": str(payload.url),
            "draft_id": generated_draft.draft_id if generated_draft else "",
        },
    )
    return EvidenceIntakeResponse(
        case=case,
        evidence_pack=evidence_pack,
        generated_draft=generated_draft,
    )
