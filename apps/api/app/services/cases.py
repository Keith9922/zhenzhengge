from datetime import datetime, timezone
from itertools import count

from app.schemas.cases import CaseCreateRequest, CaseDetail, CaseStatus, CaseSummary


_CASE_COUNTER = count(3)
_CASE_DETAILS: list[CaseDetail] = []


class CaseService:
    def __init__(self) -> None:
        now = datetime.now(timezone.utc)
        self._cases: list[CaseDetail] = _CASE_DETAILS
        if not self._cases:
            self._cases.extend(
                [
                    CaseDetail(
                        case_id="case-zhzg-0001",
                        title="阿迪达斯变体商品页疑似仿冒",
                        brand_name="阿迪达斯",
                        suspect_name="阿波达斯",
                        platform="淘宝",
                        risk_score=92,
                        risk_level="high",
                        status=CaseStatus.open,
                        updated_at=now,
                        description="展示商标近似、图文混用和商品页信息留存流程的演示案件。",
                        evidence_count=2,
                        template_count=2,
                        tags=["商标近似", "商品页", "国内电商"],
                        monitoring_scope=["taobao.com", "tmall.com"],
                    ),
                    CaseDetail(
                        case_id="case-zhzg-0002",
                        title="品牌官网页面疑似冒用",
                        brand_name="证证鸽",
                        suspect_name="zhengzhengge-style",
                        platform="品牌官网",
                        risk_score=73,
                        risk_level="medium",
                        status=CaseStatus.monitoring,
                        updated_at=now,
                        description="用于演示自动巡检、风险预警和文书辅助的样例案件。",
                        evidence_count=1,
                        template_count=1,
                        tags=["官网", "巡检", "预警"],
                        monitoring_scope=["official-site.example.com"],
                    ),
                ]
            )

    def create_case(
        self,
        payload: CaseCreateRequest,
    ) -> CaseDetail:
        now = datetime.now(timezone.utc)
        serial = next(_CASE_COUNTER)
        record = CaseDetail(
            case_id=f"case-zhzg-{serial:04d}",
            title=payload.title,
            brand_name=payload.brand_name,
            suspect_name=payload.suspect_name,
            platform=payload.platform,
            risk_score=payload.risk_score,
            risk_level=payload.risk_level,
            status=CaseStatus.open,
            updated_at=now,
            description=payload.description,
            evidence_count=0,
            template_count=0,
            tags=list(payload.tags),
            monitoring_scope=list(payload.monitoring_scope),
        )
        self._cases.append(record)
        return record

    def attach_evidence(self, case_id: str) -> CaseDetail | None:
        case = self.get_case(case_id)
        if case is None:
            return None
        case.evidence_count += 1
        case.updated_at = datetime.now(timezone.utc)
        return case

    def list_cases(
        self,
        *,
        status: CaseStatus | None = None,
        platform: str | None = None,
        limit: int = 20,
    ) -> tuple[list[CaseSummary], int]:
        items = self._cases
        if status is not None:
            items = [item for item in items if item.status == status]
        if platform is not None:
            items = [item for item in items if item.platform == platform]
        total = len(items)
        return [CaseSummary.model_validate(item) for item in items[:limit]], total

    def get_case(self, case_id: str) -> CaseDetail | None:
        for item in self._cases:
            if item.case_id == case_id:
                return item
        return None
