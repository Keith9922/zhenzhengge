from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.core.config import settings
from app.schemas.common import HealthResponse, ModuleStatus

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="健康检查")
def health(request: Request) -> HealthResponse:
    started_at = getattr(request.app.state, "started_at", datetime.now(timezone.utc))
    services = request.app.state.services
    modules = [
        ModuleStatus(**services["hermes"].health()),
        ModuleStatus(**services["playwright"].health()),
        ModuleStatus(**services["notifications"].health()),
    ]
    uptime = (datetime.now(timezone.utc) - started_at).total_seconds()
    return HealthResponse(
        service=settings.app_name,
        status="ok",
        version=settings.app_version,
        environment=settings.environment,
        timestamp=datetime.now(timezone.utc),
        uptime_seconds=uptime,
        modules=modules,
    )

