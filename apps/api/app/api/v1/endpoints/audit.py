from fastapi import APIRouter, Depends

from app.api.deps import get_audit_service
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.services.audit import AuditService

router = APIRouter()


@router.get("/logs", summary="审计日志列表")
def list_audit_logs(
    limit: int = 100,
    service: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("admin")),
) -> list[dict[str, str]]:
    rows = service.storage.list_audit_logs(actor_org_id=resolve_scope_organization(user), limit=limit)
    return [
        {
            "audit_id": row["audit_id"],
            "actor_token": (row["actor_token"] or "")[:8] + "***",
            "actor_user_id": row["actor_user_id"],
            "actor_org_id": row["actor_org_id"],
            "actor_role": row["actor_role"],
            "action": row["action"],
            "resource_type": row["resource_type"],
            "resource_id": row["resource_id"],
            "request_id": row["request_id"],
            "payload_json": row["payload_json"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
