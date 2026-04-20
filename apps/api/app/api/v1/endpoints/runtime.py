from fastapi import APIRouter, Depends

from app.api.deps import (
    get_hermes_orchestrator,
    get_notification_adapter,
    get_playwright_worker,
)
from app.api.security import CurrentUser, require_roles
from app.schemas.common import ModuleStatus
from app.services.hermes import HermesOrchestrator
from app.services.notifications import NotificationAdapter
from app.services.playwright import PlaywrightWorker

router = APIRouter()


@router.get("/modules", summary="运行时模块状态")
def runtime_modules(
    hermes: HermesOrchestrator = Depends(get_hermes_orchestrator),
    playwright: PlaywrightWorker = Depends(get_playwright_worker),
    notifications: NotificationAdapter = Depends(get_notification_adapter),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> list[ModuleStatus]:
    return [
        ModuleStatus(**hermes.health()),
        ModuleStatus(**playwright.health()),
        ModuleStatus(**notifications.health()),
    ]
