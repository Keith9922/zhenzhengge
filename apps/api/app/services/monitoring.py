from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from difflib import SequenceMatcher
import threading
from urllib.parse import urlparse

from app.core.config import Settings
from app.core.storage import SQLiteStorage
from app.schemas.cases import CaseCreateRequest, CaseDetail
from app.schemas.evidence import EvidencePackRecord
from app.schemas.monitoring import (
    MonitorTaskCreateRequest,
    MonitorTaskRecord,
    MonitorTaskStatus,
)
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.notifications import NotificationAdapter
from app.services.playwright import PlaywrightWorker


@dataclass(slots=True)
class MonitorRunResult:
    task: MonitorTaskRecord
    matched: bool
    risk_score: int
    case: CaseDetail | None = None
    evidence_pack: EvidencePackRecord | None = None
    notifications_sent: int = 0
    detail: str = ""


class MonitorTaskService:
    def __init__(
        self,
        storage: SQLiteStorage,
        *,
        case_service: CaseService,
        evidence_service: EvidenceService,
        hermes: HermesOrchestrator,
        playwright: PlaywrightWorker,
        notifications: NotificationAdapter,
        settings: Settings,
    ) -> None:
        self.storage = storage
        self.case_service = case_service
        self.evidence_service = evidence_service
        self.hermes = hermes
        self.playwright = playwright
        self.notifications = notifications
        self.settings = settings
        self._stop_event = threading.Event()
        self._scheduler_thread: threading.Thread | None = None
        self._run_lock = threading.Lock()

    def list_tasks(self) -> list[MonitorTaskRecord]:
        return self.storage.list_monitor_tasks()

    def get_task(self, task_id: str) -> MonitorTaskRecord | None:
        return self.storage.get_monitor_task(task_id)

    def create_task(self, payload: MonitorTaskCreateRequest) -> MonitorTaskRecord:
        return self.storage.create_monitor_task(payload)

    def toggle_task(self, task_id: str, enabled: bool) -> MonitorTaskRecord | None:
        return self.storage.toggle_monitor_task(task_id, enabled)

    def start_scheduler(self) -> None:
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            return
        self._stop_event.clear()
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, name="monitor-scheduler", daemon=True)
        self._scheduler_thread.start()

    def stop_scheduler(self) -> None:
        self._stop_event.set()
        if self._scheduler_thread and self._scheduler_thread.is_alive():
            self._scheduler_thread.join(timeout=2.0)

    def run_due_tasks(self) -> int:
        now = datetime.now(timezone.utc)
        triggered = 0
        for task in self.list_tasks():
            if task.status != MonitorTaskStatus.active:
                continue
            if not self._is_due(task, now):
                continue
            result = self.run_task(task.task_id, trigger="scheduler")
            if result is not None:
                triggered += 1
        return triggered

    def run_task(self, task_id: str, *, trigger: str = "manual") -> MonitorRunResult | None:
        if not self._run_lock.acquire(timeout=30):
            return None
        run_id = self.storage.create_monitor_run(task_id=task_id)
        try:
            return self._run_task_inner(task_id, run_id=run_id, trigger=trigger)
        finally:
            self._run_lock.release()

    def _run_task_inner(self, task_id: str, *, run_id: str, trigger: str) -> MonitorRunResult | None:
        task = self.storage.mark_monitor_task_run(task_id)
        if task is None:
            self.storage.finish_monitor_run(
                run_id=run_id,
                status="failed",
                risk_score=0,
                detail="监控任务不存在",
            )
            return None

        capture = self.playwright.capture(url=task.target_url, title=task.name)
        risk_score = self._calculate_risk_score(task, capture.title, capture.page_text, capture.html_content)
        if risk_score < task.risk_threshold:
            detail = (
                f"未命中阈值，trigger={trigger}，risk_score={risk_score}，threshold={task.risk_threshold}"
            )
            self.storage.finish_monitor_run(
                run_id=run_id,
                status="missed",
                risk_score=risk_score,
                detail=detail,
            )
            return MonitorRunResult(
                task=task,
                matched=False,
                risk_score=risk_score,
                detail=detail,
            )

        suspect_name = self._derive_suspect_name(task, capture.title)
        description = self._generate_case_description(task, capture, risk_score)
        case = self.case_service.create_case(
            CaseCreateRequest(
                title=capture.title or task.name,
                brand_name=self._derive_brand_name(task),
                suspect_name=suspect_name,
                platform=task.site,
                risk_score=risk_score,
                risk_level=self._risk_level(risk_score),
                description=description,
                tags=self._derive_tags(task),
                monitoring_scope=[task.target_url, task.site],
            )
        )
        _ = self.hermes.submit_capture_workflow(case.case_id)
        evidence_pack = self.evidence_service.create_pack_for_case(
            case_id=case.case_id,
            source_url=capture.source_url,
            source_title=capture.title or task.name,
            note=f"monitor-task:{task.task_id}",
            capture_channel="monitoring",
        )
        evidence_pack = self.evidence_service.persist_capture_artifacts(
            evidence_pack,
            raw_html=capture.html_content,
            screenshot_bytes=capture.screenshot_bytes,
        )
        case = self.case_service.attach_evidence(case.case_id) or case

        notification_subject = f"【证证鸽】发现新的疑似侵权线索：{case.title}"
        notification_body = (
            f"任务：{task.name}\n"
            f"站点：{task.site}\n"
            f"地址：{task.target_url}\n"
            f"风险分：{risk_score}\n"
            f"案件：{case.case_id}\n"
            f"证据包：{evidence_pack.evidence_pack_id}\n"
            f"说明：{description[:240]}"
        )
        notify_results = self.notifications.notify_enabled_channels(
            event_type="monitor_hit",
            subject=notification_subject,
            body=notification_body,
            task_id=task.task_id,
            case_id=case.case_id,
        )
        detail = "命中监控规则，已创建案件、证据包并触发通知"
        self.storage.finish_monitor_run(
            run_id=run_id,
            status="matched",
            risk_score=risk_score,
            case_id=case.case_id,
            evidence_pack_id=evidence_pack.evidence_pack_id,
            detail=detail,
        )
        return MonitorRunResult(
            task=task,
            matched=True,
            risk_score=risk_score,
            case=case,
            evidence_pack=evidence_pack,
            notifications_sent=len(notify_results),
            detail=detail,
        )

    def list_task_runs(self, task_id: str, *, limit: int = 20) -> list[dict[str, str | int | None]]:
        rows = self.storage.list_monitor_runs(task_id=task_id, limit=limit)
        return [
            {
                "run_id": row["run_id"],
                "task_id": row["task_id"],
                "started_at": row["started_at"],
                "finished_at": row["finished_at"],
                "status": row["status"],
                "risk_score": row["risk_score"],
                "case_id": row["case_id"],
                "evidence_pack_id": row["evidence_pack_id"],
                "detail": row["detail"],
            }
            for row in rows
        ]

    def _scheduler_loop(self) -> None:
        interval = max(5, int(self.settings.monitor_scheduler_interval_seconds))
        while not self._stop_event.is_set():
            try:
                self.run_due_tasks()
            except Exception:
                pass
            self._stop_event.wait(interval)

    def _generate_case_description(
        self,
        task: MonitorTaskRecord,
        capture,
        risk_score: int,
    ) -> str:
        result = self.hermes.generate_case_summary(
            case_context={
                "title": capture.title or task.name,
                "brand_name": self._derive_brand_name(task),
                "suspect_name": self._derive_suspect_name(task, capture.title),
                "platform": task.site,
                "risk_score": risk_score,
                "risk_level": self._risk_level(risk_score),
                "description": f"监控任务 {task.name} 在 {task.target_url} 命中疑似线索。",
            },
            evidence_context=[
                {
                    "source_title": capture.title or task.name,
                    "source_url": task.target_url,
                    "summary": capture.page_text[:240],
                }
            ],
            max_completion_tokens=900,
        )
        return result.content

    @staticmethod
    def _derive_brand_name(task: MonitorTaskRecord) -> str:
        if task.brand_keywords:
            return task.brand_keywords[0]
        return task.name

    @staticmethod
    def _derive_tags(task: MonitorTaskRecord) -> list[str]:
        tags = ["自动监测", task.site]
        tags.extend(task.brand_keywords[:3])
        return list(dict.fromkeys(tags))

    @staticmethod
    def _derive_suspect_name(task: MonitorTaskRecord, captured_title: str) -> str:
        title = (captured_title or "").strip()
        if title:
            return title[:60]
        parsed = urlparse(task.target_url)
        return parsed.netloc or task.site

    @staticmethod
    def _risk_level(score: int) -> str:
        if score >= 85:
            return "high"
        if score >= 60:
            return "medium"
        return "low"

    @staticmethod
    def _is_due(task: MonitorTaskRecord, now: datetime) -> bool:
        if task.last_run_at is None:
            return True
        delta = now - task.last_run_at
        return delta.total_seconds() >= task.frequency_minutes * 60

    def _calculate_risk_score(
        self,
        task: MonitorTaskRecord,
        captured_title: str,
        page_text: str,
        html_content: str,
    ) -> int:
        text = " ".join(
            part
            for part in [
                task.name.strip(),
                task.site.strip(),
                task.target_url.strip(),
                captured_title.strip(),
                page_text.strip(),
                html_content.strip(),
            ]
            if part
        ).lower()
        if not text:
            return 0
        if not task.brand_keywords:
            return 75

        scores: list[int] = []
        for keyword in task.brand_keywords:
            normalized = keyword.strip().lower()
            if not normalized:
                continue
            if normalized in text:
                scores.append(95)
                continue
            title_ratio = SequenceMatcher(None, normalized, captured_title.lower()).ratio()
            text_ratio = SequenceMatcher(None, normalized, text[: min(len(text), 800)]).ratio()
            scores.append(int(max(title_ratio, text_ratio) * 100))

        return max(scores, default=0)
