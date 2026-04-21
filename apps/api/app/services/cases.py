from datetime import datetime, timezone
import re

from app.core.storage import SQLiteStorage
from app.schemas.cases import (
    CaseActionCenterResponse,
    CaseActionItem,
    CaseCreateRequest,
    CaseDetail,
    CaseEvidenceClaimLinkItem,
    CaseEvidenceClaimLinksResponse,
    CaseInsightsResponse,
    CaseStatus,
    CaseSummary,
    EvidenceClaimReference,
)
from app.schemas.drafts import DocumentDraftRecord, DraftStatus


class CaseService:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def create_case(self, payload: CaseCreateRequest, *, organization_id: str, owner_user_id: str) -> CaseDetail:
        return self.storage.create_case(payload, organization_id=organization_id, owner_user_id=owner_user_id)

    def attach_evidence(self, case_id: str, *, organization_id: str | None = None) -> CaseDetail | None:
        return self.storage.attach_evidence(case_id, organization_id=organization_id)

    def update_description(
        self, case_id: str, description: str, *, organization_id: str | None = None
    ) -> CaseDetail | None:
        return self.storage.update_case_description(case_id, description, organization_id=organization_id)

    def list_cases(
        self,
        *,
        status: CaseStatus | None = None,
        platform: str | None = None,
        organization_id: str | None = None,
        limit: int = 20,
    ) -> tuple[list[CaseSummary], int]:
        return self.storage.list_cases(status=status, platform=platform, organization_id=organization_id, limit=limit)

    def get_case(self, case_id: str, *, organization_id: str | None = None) -> CaseDetail | None:
        return self.storage.get_case(case_id, organization_id=organization_id)

    def get_action_center(self, case_id: str, *, organization_id: str | None = None) -> CaseActionCenterResponse | None:
        case = self.storage.get_case(case_id, organization_id=organization_id)
        if case is None:
            return None

        evidence_packs = self.storage.list_evidence_packs(case_id, organization_id=organization_id)
        drafts = self.storage.list_document_drafts(case_id, organization_id=organization_id)
        items: list[CaseActionItem] = []

        if not evidence_packs:
            items.append(
                CaseActionItem(
                    action_id="collect-evidence",
                    title="补充证据包",
                    description="当前案件尚无证据包，先补全截图、HTML 与来源信息。",
                    priority="high",
                    cta_label="去证据包",
                    href=f"/workspace/evidence-packs?caseId={case_id}",
                )
            )
        else:
            items.append(
                CaseActionItem(
                    action_id="review-evidence",
                    title="复核现有证据",
                    description=f"已沉淀 {len(evidence_packs)} 个证据包，建议先核对关键页面与哈希留痕。",
                    priority="high",
                    cta_label="查看证据包",
                    href=f"/workspace/evidence-packs?caseId={case_id}",
                )
            )

        if not drafts:
            items.append(
                CaseActionItem(
                    action_id="create-draft",
                    title="生成首版文书",
                    description="当前尚无草稿，建议先生成律师函或平台投诉函初稿。",
                    priority="high",
                    cta_label="去生成草稿",
                    href=f"/workspace/drafts?caseId={case_id}",
                )
            )
        else:
            latest = drafts[0]
            if latest.status in {DraftStatus.generated, DraftStatus.rejected}:
                items.append(
                    CaseActionItem(
                        action_id="submit-review",
                        title="提交法务审核",
                        description=f"最新草稿状态为 {latest.status.value}，建议补充说明后提交审核。",
                        priority="high",
                        cta_label="去草稿详情",
                        href=f"/workspace/drafts/{latest.draft_id}",
                    )
                )
            elif latest.status == DraftStatus.submitted:
                items.append(
                    CaseActionItem(
                        action_id="approve-draft",
                        title="完成审核决策",
                        description="草稿已提交审核，建议尽快给出通过/驳回意见并固化处理动作。",
                        priority="high",
                        cta_label="去审核",
                        href=f"/workspace/drafts/{latest.draft_id}",
                    )
                )
            else:
                items.append(
                    CaseActionItem(
                        action_id="export-draft",
                        title="导出可提交材料",
                        description="草稿已通过审核，建议导出文书并进入投诉/发函动作。",
                        priority="medium",
                        cta_label="去导出",
                        href=f"/workspace/drafts/{latest.draft_id}",
                    )
                )

        if not self._has_platform_complaint_variants(drafts):
            items.append(
                CaseActionItem(
                    action_id="platform-variants",
                    title="补齐平台化投诉版本",
                    description="为淘宝/拼多多/京东生成渠道化投诉函，提升提交命中率与复用效率。",
                    priority="medium",
                    cta_label="去模板生成",
                    href=f"/workspace/drafts?caseId={case_id}",
                )
            )

        items_sorted = sorted(items, key=lambda item: {"high": 0, "medium": 1, "low": 2}.get(item.priority, 9))
        return CaseActionCenterResponse(
            case_id=case_id,
            generated_at=datetime.now(timezone.utc),
            items=items_sorted[:3],
        )

    def get_evidence_claim_links(
        self, case_id: str, *, organization_id: str | None = None
    ) -> CaseEvidenceClaimLinksResponse | None:
        case = self.storage.get_case(case_id, organization_id=organization_id)
        if case is None:
            return None

        evidence_packs = self.storage.list_evidence_packs(case_id, organization_id=organization_id)
        drafts = self.storage.list_document_drafts(case_id, organization_id=organization_id)
        grouped_claims: dict[str, list[EvidenceClaimReference]] = {}
        total_claims = 0

        for draft in drafts:
            for evidence_id, line_no, claim_text in self._extract_evidence_claims(draft):
                grouped_claims.setdefault(evidence_id, []).append(
                    EvidenceClaimReference(
                        draft_id=draft.draft_id,
                        draft_title=draft.title,
                        line_no=line_no,
                        claim_text=claim_text,
                    )
                )
                total_claims += 1

        items: list[CaseEvidenceClaimLinkItem] = []
        for pack in evidence_packs:
            claims = grouped_claims.get(pack.evidence_pack_id, [])
            items.append(
                CaseEvidenceClaimLinkItem(
                    evidence_pack_id=pack.evidence_pack_id,
                    source_title=pack.source_title,
                    claim_count=len(claims),
                    claims=claims,
                )
            )

        return CaseEvidenceClaimLinksResponse(
            case_id=case_id,
            generated_at=datetime.now(timezone.utc),
            total_evidence=len(evidence_packs),
            total_claims=total_claims,
            items=items,
        )

    def get_insights(self, *, organization_id: str | None = None) -> CaseInsightsResponse:
        case_where = "WHERE organization_id = ?" if organization_id else ""
        draft_where = "WHERE organization_id = ?" if organization_id else ""
        org_params = (organization_id,) if organization_id else ()
        with self.storage.connect() as conn:
            total_cases = int(
                conn.execute(f"SELECT COUNT(*) FROM cases {case_where}", org_params).fetchone()[0] or 0
            )
            acted_cases = int(
                conn.execute(
                    f"""
                    SELECT COUNT(DISTINCT case_id)
                    FROM document_drafts
                    {draft_where}
                    {"AND" if draft_where else "WHERE"}
                    status IN ('submitted', 'approved', 'exported')
                    """,
                    org_params,
                ).fetchone()[0]
                or 0
            )
            reviewed_total = int(
                conn.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM document_drafts
                    {draft_where}
                    {"AND" if draft_where else "WHERE"}
                    status IN ('submitted', 'approved', 'exported')
                    """,
                    org_params,
                ).fetchone()[0]
                or 0
            )
            reviewed_pass = int(
                conn.execute(
                    f"""
                    SELECT COUNT(*)
                    FROM document_drafts
                    {draft_where}
                    {"AND" if draft_where else "WHERE"}
                    status IN ('approved', 'exported')
                    """,
                    org_params,
                ).fetchone()[0]
                or 0
            )
            tta_params: list[str] = []
            tta_sql = """
                SELECT e.case_id, MIN(e.created_at) AS first_evidence_at, MIN(d.updated_at) AS first_export_at
                FROM evidence_packs e
                JOIN document_drafts d ON d.case_id = e.case_id
                WHERE d.export_path IS NOT NULL
            """
            if organization_id:
                tta_sql += " AND d.organization_id = ? AND e.organization_id = ?"
                tta_params.extend([organization_id, organization_id])
            tta_sql += " GROUP BY e.case_id"
            tta_rows = conn.execute(tta_sql, tuple(tta_params)).fetchall()

        tta_values: list[float] = []
        for row in tta_rows:
            first_evidence_at = row["first_evidence_at"]
            first_export_at = row["first_export_at"]
            if not first_evidence_at or not first_export_at:
                continue
            start = datetime.fromisoformat(first_evidence_at)
            end = datetime.fromisoformat(first_export_at)
            hours = (end - start).total_seconds() / 3600
            if hours >= 0:
                tta_values.append(hours)

        action_rate = round((acted_cases / total_cases) * 100, 2) if total_cases else 0.0
        evidence_pass_rate = round((reviewed_pass / reviewed_total) * 100, 2) if reviewed_total else 0.0
        tta_hours = round(sum(tta_values) / len(tta_values), 2) if tta_values else None

        return CaseInsightsResponse(
            generated_at=datetime.now(timezone.utc),
            total_cases=total_cases,
            cases_with_actions=acted_cases,
            action_rate=action_rate,
            evidence_pass_rate=evidence_pass_rate,
            tta_hours=tta_hours,
        )

    @staticmethod
    def _has_platform_complaint_variants(drafts: list[DocumentDraftRecord]) -> bool:
        keys = {draft.template_key for draft in drafts}
        required = {
            "platform-complaint-taobao",
            "platform-complaint-pinduoduo",
            "platform-complaint-jd",
        }
        return bool(keys.intersection(required))

    @staticmethod
    def _extract_evidence_claims(draft: DocumentDraftRecord) -> list[tuple[str, int, str]]:
        pattern = re.compile(r"EvidenceID\s*=\s*([A-Za-z0-9_-]+)")
        results: list[tuple[str, int, str]] = []
        for index, raw_line in enumerate((draft.content or "").splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            for evidence_id in pattern.findall(line):
                results.append((evidence_id, index, line[:240]))
        return results
