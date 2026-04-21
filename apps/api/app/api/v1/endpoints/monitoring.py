from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_audit_service, get_monitor_task_service
from app.api.security import CurrentUser, require_roles, resolve_scope_organization
from app.schemas.common import ApiMessage
from app.schemas.monitoring import (
    MonitorTaskCreateRequest,
    MonitorTaskListResponse,
    MonitorTaskRecord,
    MonitorTaskToggleRequest,
)
from app.services.monitoring import MonitorTaskService
from app.services.audit import AuditService

router = APIRouter()


@router.get("", response_model=MonitorTaskListResponse, summary="监控任务列表")
def list_monitor_tasks(
    service: MonitorTaskService = Depends(get_monitor_task_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> MonitorTaskListResponse:
    items = service.list_tasks(organization_id=resolve_scope_organization(user))
    return MonitorTaskListResponse(total=len(items), items=items)


@router.post("", response_model=MonitorTaskRecord, summary="创建监控任务")
def create_monitor_task(
    payload: MonitorTaskCreateRequest,
    service: MonitorTaskService = Depends(get_monitor_task_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> MonitorTaskRecord:
    scope_org = resolve_scope_organization(user) or user.organization_id
    item = service.create_task(payload, organization_id=scope_org, owner_user_id=user.user_id)
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="monitor.create",
        resource_type="monitor_task",
        resource_id=item.task_id,
        payload={"target_url": str(payload.target_url), "site": payload.site},
    )
    return item


@router.get("/{task_id}", response_model=MonitorTaskRecord, summary="监控任务详情")
def get_monitor_task(
    task_id: str,
    service: MonitorTaskService = Depends(get_monitor_task_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> MonitorTaskRecord:
    item = service.get_task(task_id, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    return item


@router.get("/{task_id}/runs", summary="监控任务执行历史")
def list_monitor_task_runs(
    task_id: str,
    limit: int = 20,
    service: MonitorTaskService = Depends(get_monitor_task_service),
    user: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> list[dict[str, str | int | None]]:
    scope_org = resolve_scope_organization(user)
    if service.get_task(task_id, organization_id=scope_org) is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    return service.list_task_runs(task_id=task_id, organization_id=scope_org, limit=limit)


@router.post("/{task_id}/toggle", response_model=MonitorTaskRecord, summary="启停监控任务")
def toggle_monitor_task(
    task_id: str,
    payload: MonitorTaskToggleRequest,
    service: MonitorTaskService = Depends(get_monitor_task_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> MonitorTaskRecord:
    item = service.toggle_task(task_id, payload.enabled, organization_id=resolve_scope_organization(user))
    if item is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="monitor.toggle",
        resource_type="monitor_task",
        resource_id=task_id,
        payload={"enabled": payload.enabled},
    )
    return item


@router.post("/{task_id}/run", response_model=ApiMessage, summary="手动执行一次监控任务")
def run_monitor_task(
    task_id: str,
    service: MonitorTaskService = Depends(get_monitor_task_service),
    audit: AuditService = Depends(get_audit_service),
    user: CurrentUser = Depends(require_roles("operator", "admin")),
) -> ApiMessage:
    result = service.run_task(
        task_id,
        organization_id=resolve_scope_organization(user),
        owner_user_id=user.user_id,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="监控任务不存在")
    audit.log(
        actor_token=user.token,
        actor_user_id=user.user_id,
        actor_org_id=user.organization_id,
        actor_role=user.role,
        action="monitor.run",
        resource_type="monitor_task",
        resource_id=task_id,
        payload={
            "matched": result.matched,
            "risk_score": result.risk_score,
            "detail": result.detail,
            "case_id": result.case.case_id if result.case else "",
        },
    )
    if not result.matched:
        return ApiMessage(message=f"监控任务已执行：{result.task.name}；{result.detail}")

    case_id = result.case.case_id if result.case else "unknown"
    evidence_pack_id = result.evidence_pack.evidence_pack_id if result.evidence_pack else "unknown"
    return ApiMessage(
        message=(
            f"监控命中：{result.task.name}；"
            f"risk={result.risk_score}；"
            f"case={case_id}；"
            f"evidence={evidence_pack_id}；"
            f"notifications={result.notifications_sent}"
        )
    )
