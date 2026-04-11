from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_monitor_task_service
from app.schemas.common import ApiMessage
from app.schemas.monitoring import (
    MonitorTaskCreateRequest,
    MonitorTaskListResponse,
    MonitorTaskRecord,
    MonitorTaskToggleRequest,
)
from app.services.monitoring import MonitorTaskService

router = APIRouter()


@router.get("", response_model=MonitorTaskListResponse, summary="监控任务列表")
def list_monitor_tasks(
    service: MonitorTaskService = Depends(get_monitor_task_service),
) -> MonitorTaskListResponse:
    items = service.list_tasks()
    return MonitorTaskListResponse(total=len(items), items=items)


@router.post("", response_model=MonitorTaskRecord, summary="创建监控任务")
def create_monitor_task(
    payload: MonitorTaskCreateRequest,
    service: MonitorTaskService = Depends(get_monitor_task_service),
) -> MonitorTaskRecord:
    return service.create_task(payload)


@router.get("/{task_id}", response_model=MonitorTaskRecord, summary="监控任务详情")
def get_monitor_task(
    task_id: str,
    service: MonitorTaskService = Depends(get_monitor_task_service),
) -> MonitorTaskRecord:
    item = service.get_task(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    return item


@router.post("/{task_id}/toggle", response_model=MonitorTaskRecord, summary="启停监控任务")
def toggle_monitor_task(
    task_id: str,
    payload: MonitorTaskToggleRequest,
    service: MonitorTaskService = Depends(get_monitor_task_service),
) -> MonitorTaskRecord:
    item = service.toggle_task(task_id, payload.enabled)
    if item is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    return item


@router.post("/{task_id}/run", response_model=ApiMessage, summary="手动执行一次监控任务")
def run_monitor_task(
    task_id: str,
    service: MonitorTaskService = Depends(get_monitor_task_service),
) -> ApiMessage:
    item = service.mark_run(task_id)
    if item is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    return ApiMessage(message=f"监控任务已执行：{item.name}")
