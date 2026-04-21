from app.schemas.cases import CaseDetail, CaseCreateRequest
from app.schemas.drafts import DocumentDraftCreateRequest, DocumentDraftRecord
from app.schemas.evidence import EvidencePackRecord
from app.schemas.intake import EvidenceIntakeRequest
from app.services.brand_profiles import BrandProfileService
from app.services.cases import CaseService
from app.services.drafts import DocumentDraftService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.playwright import PlaywrightWorker


class IntakeService:
    def __init__(
        self,
        *,
        case_service: CaseService,
        evidence_service: EvidenceService,
        draft_service: DocumentDraftService,
        hermes: HermesOrchestrator,
        playwright: PlaywrightWorker,
        brand_profile_service: BrandProfileService | None = None,
    ) -> None:
        self.case_service = case_service
        self.evidence_service = evidence_service
        self.draft_service = draft_service
        self.hermes = hermes
        self.playwright = playwright
        self.brand_profile_service = brand_profile_service

    def intake(
        self,
        payload: EvidenceIntakeRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> tuple[CaseDetail, EvidencePackRecord, DocumentDraftRecord | None]:
        full_text = " ".join([payload.title, payload.page_text, payload.html])
        # 优先从品牌档案匹配 brand_name 和评分关键词
        profile_brand = None
        profile_keywords: list[str] = []
        if self.brand_profile_service:
            profile_brand = self.brand_profile_service.match_brand_for_text(full_text, organization_id)
            profile_keywords = self.brand_profile_service.get_risk_keywords_for_org(organization_id)

        brand_name = profile_brand or self._derive_brand_name(payload.title)
        suspect_name = self._derive_suspect_name(payload.title)
        platform = self._derive_platform(payload.source)
        description = self._derive_description(payload.page_text, payload.html, payload.request_id)
        monitoring_scope = self._derive_monitoring_scope(str(payload.url), payload.source)
        tags = self._derive_tags(payload.title, payload.source)
        risk_score = self._estimate_risk(payload.title, payload.page_text, payload.html, profile_keywords)
        risk_level = self._risk_level(risk_score)

        case = self.case_service.create_case(
            CaseCreateRequest(
                title=payload.title,
                brand_name=brand_name,
                suspect_name=suspect_name,
                platform=platform,
                risk_score=risk_score,
                risk_level=risk_level,
                description=description,
                tags=tags,
                monitoring_scope=monitoring_scope,
            ),
            organization_id=organization_id,
            owner_user_id=owner_user_id,
        )
        capture = None
        needs_capture = not payload.html.strip() or not payload.screenshot_base64.strip()
        if needs_capture:
            capture = self.playwright.capture(url=str(payload.url), title=payload.title)
        evidence = self.evidence_service.create_pack_for_case(
            case_id=case.case_id,
            organization_id=organization_id,
            owner_user_id=owner_user_id,
            source_url=str(payload.url),
            source_title=payload.title,
            note=payload.request_id,
            capture_channel=payload.source or "browser_extension",
        )
        persisted = self.evidence_service.persist_capture_artifacts(
            evidence,
            raw_html=payload.html or (capture.html_content if capture else ""),
            screenshot_base64=payload.screenshot_base64,
            screenshot_bytes=capture.screenshot_bytes if capture else None,
            organization_id=organization_id,
        )
        evidence = persisted
        workflow = self.hermes.submit_capture_workflow(
            case.case_id,
            case_context={
                "case_id": case.case_id,
                "title": case.title,
                "brand_name": case.brand_name,
                "suspect_name": case.suspect_name,
                "platform": case.platform,
                "risk_level": case.risk_level,
                "description": case.description,
            },
            evidence_context=[{
                "evidence_pack_id": evidence.evidence_pack_id,
                "source_url": evidence.source_url,
                "source_title": evidence.source_title,
                "chain_sha256": evidence.chain_sha256,
                "page_text": payload.page_text[:400],
            }],
        )
        if workflow.status == "completed" and workflow.detail:
            updated = self.case_service.update_description(
                case.case_id, workflow.detail, organization_id=organization_id
            )
            if updated:
                case = updated
        refreshed_case = self.case_service.attach_evidence(case.case_id, organization_id=organization_id)
        active_case = refreshed_case or case
        generated_draft = self._maybe_generate_draft(
            active_case,
            payload,
            organization_id=organization_id,
            owner_user_id=owner_user_id,
        )
        return active_case, evidence, generated_draft

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

    @staticmethod
    def _estimate_risk(title: str, page_text: str, html: str, extra_keywords: list[str] | None = None) -> int:
        text = " ".join([title, page_text, html]).lower()
        score = 45
        base_keywords = ["侵权", "仿", "高仿", "山寨", "官方", "旗舰", "正品", "adidas", "nike", "商标", "专利"]
        all_keywords = base_keywords + [kw.lower() for kw in (extra_keywords or [])]
        hits = sum(1 for keyword in all_keywords if keyword in text)
        score += min(50, hits * 6)
        if "example.com" in text:
            score -= 20
        return max(0, min(100, score))

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 85:
            return "high"
        if score >= 60:
            return "medium"
        return "low"

    def _maybe_generate_draft(
        self,
        case: CaseDetail,
        payload: EvidenceIntakeRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> DocumentDraftRecord | None:
        if not payload.auto_generate_draft:
            return None

        template_key = (payload.draft_template_key or "lawyer-letter").strip() or "lawyer-letter"
        try:
            return self.draft_service.generate_draft(
                DocumentDraftCreateRequest(
                    case_id=case.case_id,
                    template_key=template_key,
                    variables_override={
                        "取证时间": payload.captured_at.isoformat(),
                        "取证渠道": payload.source or "browser-extension",
                        "取证请求编号": payload.request_id,
                        "证据留存说明": "当前证据包含网页抓取、截图、HTML 与哈希链；如已启用可信时间戳，将同步生成可下载回执。",
                    },
                ),
                organization_id=organization_id,
                owner_user_id=owner_user_id,
            )
        except ValueError:
            return None
