from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_notification_adapter
from app.schemas.common import ApiMessage
from app.schemas.notification_channels import (
    NotificationChannelCreateRequest,
    NotificationChannelListResponse,
    NotificationChannelRecord,
    NotificationChannelTestRequest,
)
from app.services.notifications import NotificationAdapter

router = APIRouter()


@router.get("/logs", summary="通知日志列表")
def list_logs(
    limit: int = 50,
    service: NotificationAdapter = Depends(get_notification_adapter),
) -> list[dict[str, str | None]]:
    return service.list_logs(limit=limit)


@router.get("", response_model=NotificationChannelListResponse, summary="通知渠道列表")
def list_channels(
    service: NotificationAdapter = Depends(get_notification_adapter),
) -> NotificationChannelListResponse:
    items = service.list_channels()
    return NotificationChannelListResponse(total=len(items), items=items)


@router.post("", response_model=NotificationChannelRecord, summary="新增通知渠道")
def create_channel(
    payload: NotificationChannelCreateRequest,
    service: NotificationAdapter = Depends(get_notification_adapter),
) -> NotificationChannelRecord:
    return service.create_channel(payload)


@router.post("/{channel_id}/test", response_model=ApiMessage, summary="测试通知渠道")
def test_channel(
    channel_id: str,
    payload: NotificationChannelTestRequest,
    service: NotificationAdapter = Depends(get_notification_adapter),
) -> ApiMessage:
    try:
        result = service.test_channel(channel_id, subject=payload.subject, body=payload.body)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"通知测试失败：{exc}") from exc
    return ApiMessage(message=result["detail"])
