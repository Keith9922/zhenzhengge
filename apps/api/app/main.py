from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.storage import SQLiteStorage
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.notifications import NotificationAdapter
from app.services.playwright import PlaywrightWorker
from app.services.intake import IntakeService
from app.services.templates import DocumentTemplateService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = datetime.now(timezone.utc)
    app.state.storage = SQLiteStorage(app.state.settings.database_url)
    app.state.services = {
        "cases": CaseService(app.state.storage),
        "evidence": EvidenceService(app.state.storage),
        "templates": DocumentTemplateService(),
        "hermes": HermesOrchestrator(),
        "playwright": PlaywrightWorker(),
        "notifications": NotificationAdapter(),
        "intake": None,
    }
    app.state.services["intake"] = IntakeService(
        case_service=app.state.services["cases"],
        evidence_service=app.state.services["evidence"],
        hermes=app.state.services["hermes"],
        playwright=app.state.services["playwright"],
    )
    yield


def create_app(settings_obj: Settings | None = None) -> FastAPI:
    active_settings = settings_obj or get_settings()
    app = FastAPI(
        title=active_settings.app_name,
        version=active_settings.app_version,
        description="证证鸽后端骨架：案件、证据包、文书模板、通知与工作流编排预留位。",
        docs_url="/docs" if active_settings.enable_docs else None,
        redoc_url=None,
        lifespan=lifespan,
    )
    app.state.settings = active_settings

    app.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_origin_regex=active_settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=active_settings.api_v1_prefix)
    app.include_router(health_router)

    @app.get("/", summary="服务入口")
    def root() -> dict[str, str]:
        return {
            "service": active_settings.app_name,
            "status": "ok",
            "docs": "/docs" if active_settings.enable_docs else "disabled",
            "api_prefix": active_settings.api_v1_prefix,
        }

    return app


app = create_app()
