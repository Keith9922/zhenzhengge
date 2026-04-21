from fastapi import APIRouter, Depends

from app.api.deps import (
    get_app_settings,
    get_evidence_service,
    get_hermes_orchestrator,
    get_notification_adapter,
    get_playwright_worker,
)
from app.api.security import CurrentUser, require_roles
from app.core.config import Settings
from app.schemas.common import ModuleStatus, RuntimeComplianceResponse
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.notifications import NotificationAdapter
from app.services.playwright import PlaywrightWorker

router = APIRouter()


@router.get("/modules", summary="运行时模块状态")
def runtime_modules(
    hermes: HermesOrchestrator = Depends(get_hermes_orchestrator),
    evidence: EvidenceService = Depends(get_evidence_service),
    playwright: PlaywrightWorker = Depends(get_playwright_worker),
    notifications: NotificationAdapter = Depends(get_notification_adapter),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> list[ModuleStatus]:
    return [
        ModuleStatus(**hermes.health()),
        ModuleStatus(**evidence.timestamp_health()),
        ModuleStatus(**playwright.health()),
        ModuleStatus(**notifications.health()),
    ]


@router.get("/compliance", response_model=RuntimeComplianceResponse, summary="合规开关状态")
def runtime_compliance(
    settings: Settings = Depends(get_app_settings),
    evidence: EvidenceService = Depends(get_evidence_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> RuntimeComplianceResponse:
    warnings: list[str] = []

    if not settings.require_auth:
        warnings.append("当前鉴权已关闭，正式环境应开启 ZHZG_REQUIRE_AUTH=true。")
    if settings.enable_demo_seed:
        warnings.append("当前 Demo Seed 已开启，正式环境应关闭 ZHZG_ENABLE_DEMO_SEED。")
    if not settings.draft_generation_strict:
        warnings.append("文书严格模式已关闭，建议开启 ZHZG_DRAFT_GENERATION_STRICT=true。")
    if settings.capture_allow_http_fallback:
        warnings.append("HTTP 回退已开启，取证失败时会降级抓取，建议在法证场景谨慎使用。")
    if settings.llm_provider.strip().lower() in {"", "stub", "placeholder", "disabled", "off"}:
        warnings.append("当前 LLM 提供方不可用，无法生成可信文书草稿。")
    if not settings.extension_api_token:
        warnings.append("未配置独立扩展 Token（ZHZG_EXTENSION_API_TOKEN），建议在生产环境启用。")
    if settings.evidence_timestamp_enabled and not settings.evidence_timestamp_tsa_url:
        warnings.append("可信时间戳已启用但未配置 TSA 地址（ZHZG_EVIDENCE_TIMESTAMP_TSA_URL）。")
    if settings.evidence_timestamp_required and not settings.evidence_timestamp_enabled:
        warnings.append("已开启强制时间戳但时间戳功能未启用，取证会失败。")

    llm_ready = settings.llm_provider.strip().lower() not in {"", "stub", "placeholder", "disabled", "off"}
    timestamp_health = evidence.timestamp_health()
    timestamp_ready = timestamp_health["status"] == "ready"
    compliance_ready = (
        settings.require_auth
        and (not settings.enable_demo_seed)
        and settings.draft_generation_strict
        and ((not settings.evidence_timestamp_required) or timestamp_ready)
    )

    return RuntimeComplianceResponse(
        require_auth=settings.require_auth,
        demo_seed_enabled=settings.enable_demo_seed,
        draft_generation_strict=settings.draft_generation_strict,
        capture_allow_http_fallback=settings.capture_allow_http_fallback,
        harness_agent_enabled=settings.harness_agent_enabled,
        evidence_timestamp_enabled=settings.evidence_timestamp_enabled,
        evidence_timestamp_required=settings.evidence_timestamp_required,
        evidence_timestamp_ready=timestamp_ready,
        extension_token_configured=bool(settings.extension_api_token),
        llm_provider=settings.llm_provider,
        llm_ready=llm_ready,
        compliance_ready=compliance_ready,
        warnings=warnings,
    )
