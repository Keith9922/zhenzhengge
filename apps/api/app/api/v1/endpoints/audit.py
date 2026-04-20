from fastapi import APIRouter, Depends

from app.api.deps import get_audit_service
from app.api.security import CurrentUser, require_roles
from app.services.audit import AuditService

router = APIRouter()


@router.get("/logs", summary="审计日志列表")
def list_audit_logs(
    limit: int = 100,
    service: AuditService = Depends(get_audit_service),
    _: CurrentUser = Depends(require_roles("admin")),
) -> list[dict[str, str]]:
    rows = service.storage.list_audit_logs(limit=limit)
    return [
        {
            "audit_id": row["audit_id"],
            "actor_token": row["actor_token"],
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
