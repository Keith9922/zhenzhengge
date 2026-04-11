from fastapi import Request

from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.intake import IntakeService
from app.services.hermes import HermesOrchestrator
from app.services.notifications import NotificationAdapter
from app.services.playwright import PlaywrightWorker
from app.services.templates import DocumentTemplateService


def get_case_service(request: Request) -> CaseService:
    return request.app.state.services["cases"]


def get_evidence_service(request: Request) -> EvidenceService:
    return request.app.state.services["evidence"]


def get_template_service(request: Request) -> DocumentTemplateService:
    return request.app.state.services["templates"]


def get_hermes_orchestrator(request: Request) -> HermesOrchestrator:
    return request.app.state.services["hermes"]


def get_playwright_worker(request: Request) -> PlaywrightWorker:
    return request.app.state.services["playwright"]


def get_notification_adapter(request: Request) -> NotificationAdapter:
    return request.app.state.services["notifications"]


def get_intake_service(request: Request) -> IntakeService:
    return request.app.state.services["intake"]
