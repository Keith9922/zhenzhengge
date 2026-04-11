from app.schemas.cases import CaseDetail, CaseCreateRequest
from app.schemas.evidence import EvidencePackRecord
from app.schemas.intake import EvidenceIntakeRequest
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.playwright import PlaywrightWorker


class IntakeService:
    def __init__(
        self,
        *,
        case_service: CaseService,
        evidence_service: EvidenceService,
        hermes: HermesOrchestrator,
        playwright: PlaywrightWorker,
    ) -> None:
        self.case_service = case_service
        self.evidence_service = evidence_service
        self.hermes = hermes
        self.playwright = playwright

    def intake(self, payload: EvidenceIntakeRequest) -> tuple[CaseDetail, EvidencePackRecord]:
        brand_name = self._derive_brand_name(payload.title)
        suspect_name = self._derive_suspect_name(payload.title)
        platform = self._derive_platform(payload.source)
        description = self._derive_description(payload.page_text, payload.html, payload.request_id)
        monitoring_scope = self._derive_monitoring_scope(str(payload.url), payload.source)
        tags = self._derive_tags(payload.title, payload.source)

        case = self.case_service.create_case(
            CaseCreateRequest(
                title=payload.title,
                brand_name=brand_name,
                suspect_name=suspect_name,
                platform=platform,
                risk_score=88,
                risk_level="high",
                description=description,
                tags=tags,
                monitoring_scope=monitoring_scope,
            )
        )
        _ = self.hermes.submit_capture_workflow(case.case_id)
        _ = self.playwright.capture(url=str(payload.url), title=payload.title)
        evidence = self.evidence_service.create_pack_for_case(
            case_id=case.case_id,
            source_url=str(payload.url),
            source_title=payload.title,
            note=payload.request_id,
            capture_channel=payload.source or "browser_extension",
        )
        self.case_service.attach_evidence(case.case_id)
        return case, evidence

    @staticmethod
    def _derive_brand_name(title: str) -> str:
        return title.strip() or "未命名品牌"

    @staticmethod
    def _derive_suspect_name(title: str) -> str:
        return f"{title.strip()}-疑似主体" if title.strip() else "未知疑似主体"

    @staticmethod
    def _derive_platform(source: str | None) -> str:
        if not source:
            return "browser-extension"
        return source

    @staticmethod
    def _derive_description(page_text: str, html: str, request_id: str) -> str:
        text = page_text.strip() or "插件提交原始取证载荷。"
        html_hint = "含 HTML" if html.strip() else "无 HTML"
        return f"{text[:180]} | {html_hint} | request_id={request_id}"

    @staticmethod
    def _derive_monitoring_scope(url: str, source: str | None) -> list[str]:
        scope = [url]
        if source:
            scope.append(source)
        return scope

    @staticmethod
    def _derive_tags(title: str, source: str | None) -> list[str]:
        tags = ["插件取证"]
        if source:
            tags.append(source)
        if title:
            tags.append(title[:20])
        return tags
