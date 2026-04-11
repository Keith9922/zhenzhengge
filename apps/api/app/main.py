from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints.health import router as health_router
from app.core.config import settings
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.notifications import NotificationAdapter
from app.services.playwright import PlaywrightWorker
from app.services.templates import DocumentTemplateService


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = datetime.now(timezone.utc)
    app.state.services = {
        "cases": CaseService(),
        "evidence": EvidenceService(),
        "templates": DocumentTemplateService(),
        "hermes": HermesOrchestrator(),
        "playwright": PlaywrightWorker(),
        "notifications": NotificationAdapter(),
    }
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="证证鸽后端骨架：案件、证据包、文书模板、通知与工作流编排预留位。",
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url=None,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(health_router)

    @app.get("/", summary="服务入口")
    def root() -> dict[str, str]:
        return {
            "service": settings.app_name,
            "status": "ok",
            "docs": "/docs" if settings.enable_docs else "disabled",
            "api_prefix": settings.api_v1_prefix,
        }

    return app


app = create_app()
