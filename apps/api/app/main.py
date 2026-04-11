from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints.health import router as health_router
from app.core.config import Settings, get_settings
from app.core.storage import SQLiteStorage
from app.services.cases import CaseService
from app.services.drafts import DocumentDraftService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.llm import OpenAICompatibleLLMService
from app.services.notifications import NotificationAdapter
from app.services.monitoring import MonitorTaskService
from app.services.playwright import PlaywrightWorker
from app.services.intake import IntakeService
from app.services.templates import DocumentTemplateService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = datetime.now(timezone.utc)
    app.state.storage = SQLiteStorage(
        app.state.settings.database_url,
        seed_demo=app.state.settings.enable_demo_seed,
    )
    llm_service = OpenAICompatibleLLMService(app.state.settings)
    app.state.services = {
        "cases": CaseService(app.state.storage),
        "evidence": EvidenceService(app.state.storage),
        "templates": DocumentTemplateService(),
        "hermes": HermesOrchestrator(llm_service=llm_service),
        "playwright": PlaywrightWorker(base_dir=app.state.storage.base_dir),
        "notifications": NotificationAdapter(app.state.storage, app.state.settings),
        "monitoring": None,
        "intake": None,
        "drafts": None,
    }
    app.state.services["drafts"] = DocumentDraftService(
        app.state.storage,
        case_service=app.state.services["cases"],
        template_service=app.state.services["templates"],
        evidence_service=app.state.services["evidence"],
        hermes=app.state.services["hermes"],
    )
    app.state.services["monitoring"] = MonitorTaskService(
        app.state.storage,
        case_service=app.state.services["cases"],
        evidence_service=app.state.services["evidence"],
        hermes=app.state.services["hermes"],
        playwright=app.state.services["playwright"],
        notifications=app.state.services["notifications"],
    )
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
        description="证证鸽后端：案件、证据包、监控任务、通知配置与文书草稿服务。",
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
