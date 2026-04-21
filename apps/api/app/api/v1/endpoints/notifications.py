from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_audit_service, get_notification_adapter
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.schemas.common import ApiMessage
from app.schemas.notification_channels import (
    NotificationChannelCreateRequest,
    NotificationChannelListResponse,
    NotificationChannelRecord,
    NotificationChannelTestRequest,
)
from app.services.notifications import NotificationAdapter
from app.services.audit import AuditService

router = APIRouter()


@router.get("/logs", summary="通知日志列表")
def list_logs(
    limit: int = 50,
    service: NotificationAdapter = Depends(get_notification_adapter),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> list[dict[str, str | None]]:
    return service.list_logs(organization_id=resolve_scope_organization(user), limit=limit)


@router.get("", response_model=NotificationChannelListResponse, summary="通知渠道列表")
def list_channels(
    service: NotificationAdapter = Depends(get_notification_adapter),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> NotificationChannelListResponse:
    items = service.list_channels(organization_id=resolve_scope_organization(user))
    return NotificationChannelListResponse(total=len(items), items=items)


@router.post("", response_model=NotificationChannelRecord, summary="新增通知渠道")
def create_channel(
    payload: NotificationChannelCreateRequest,
    service: NotificationAdapter = Depends(get_notification_adapter),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("admin")),
) -> NotificationChannelRecord:
    scope_org = resolve_scope_organization(user) or user.organization_id
    item = service.create_channel(payload, organization_id=scope_org, owner_user_id=user.user_id)
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="notification_channel.create",
        resource_type="notification_channel",
        resource_id=item.channel_id,
        payload={"channel_type": item.channel_type.value, "target": item.target},
    )
    return item


@router.post("/{channel_id}/test", response_model=ApiMessage, summary="测试通知渠道")
def test_channel(
    channel_id: str,
    payload: NotificationChannelTestRequest,
    service: NotificationAdapter = Depends(get_notification_adapter),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> ApiMessage:
    scope_org = resolve_scope_organization(user) or user.organization_id
    try:
        result = service.test_channel(
            channel_id,
            organization_id=scope_org,
            subject=payload.subject,
            body=payload.body,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"通知测试失败：{exc}") from exc
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="notification_channel.test",
        resource_type="notification_channel",
        resource_id=channel_id,
        payload={"subject": payload.subject, "status": result["status"]},
    )
    return ApiMessage(message=result["detail"])
