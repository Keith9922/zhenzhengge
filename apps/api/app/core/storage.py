from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from app.schemas.cases import CaseCreateRequest, CaseDetail, CaseStatus, CaseSummary
from app.schemas.drafts import DocumentDraftRecord, DraftStatus
from app.schemas.evidence import EvidencePackCreateRequest, EvidencePackRecord
from app.schemas.monitoring import MonitorTaskCreateRequest, MonitorTaskRecord, MonitorTaskStatus
from app.schemas.notification_channels import (
    NotificationChannelCreateRequest,
    NotificationChannelRecord,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_sqlite_path(db_url: str) -> str:
    if db_url == "sqlite:///:memory:":
        return ":memory:"
    if not db_url.startswith("sqlite:///"):
        raise ValueError("Only sqlite:/// URLs are supported in this skeleton")
    raw_path = db_url.removeprefix("sqlite:///")
    return raw_path or ":memory:"


@dataclass
class SQLiteStorage:
    db_url: str
    seed_demo: bool = True

    def __post_init__(self) -> None:
        self.db_path = _parse_sqlite_path(self.db_url)
        if self.db_path != ":memory:":
            path_obj = Path(self.db_path)
            if path_obj.parent and str(path_obj.parent) not in {"", "."}:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()
        if self.seed_demo:
            self.seed_demo_data()

    @property
    def base_dir(self) -> Path:
        if self.db_path == ":memory:":
            return Path.cwd()
        return Path(self.db_path).resolve().parent

    @contextmanager
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def ensure_schema(self) -> None:
        with self.connect() as conn:
            conn.executescript(
                """
                PRAGMA journal_mode=WAL;

                CREATE TABLE IF NOT EXISTS cases (
                    case_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    brand_name TEXT NOT NULL,
                    suspect_name TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    risk_score INTEGER NOT NULL,
                    risk_level TEXT NOT NULL,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    description TEXT NOT NULL,
                    evidence_count INTEGER NOT NULL DEFAULT 0,
                    template_count INTEGER NOT NULL DEFAULT 0,
                    tags_json TEXT NOT NULL DEFAULT '[]',
                    monitoring_scope_json TEXT NOT NULL DEFAULT '[]'
                );

                CREATE TABLE IF NOT EXISTS evidence_packs (
                    evidence_pack_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    source_title TEXT NOT NULL,
                    capture_channel TEXT NOT NULL,
                    note TEXT,
                    hash_sha256 TEXT NOT NULL,
                    snapshot_path TEXT NOT NULL,
                    html_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    FOREIGN KEY(case_id) REFERENCES cases(case_id)
                );

                CREATE TABLE IF NOT EXISTS document_drafts (
                    draft_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    template_key TEXT NOT NULL,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    review_comment TEXT,
                    export_path TEXT,
                    FOREIGN KEY(case_id) REFERENCES cases(case_id)
                );

                CREATE TABLE IF NOT EXISTS monitor_tasks (
                    task_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    target_url TEXT NOT NULL,
                    target_type TEXT NOT NULL,
                    site TEXT NOT NULL,
                    brand_keywords_json TEXT NOT NULL DEFAULT '[]',
                    frequency_minutes INTEGER NOT NULL,
                    risk_threshold INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    last_run_at TEXT
                );

                CREATE TABLE IF NOT EXISTS notification_channels (
                    channel_id TEXT PRIMARY KEY,
                    channel_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notification_logs (
                    log_id TEXT PRIMARY KEY,
                    channel_id TEXT NOT NULL,
                    task_id TEXT,
                    case_id TEXT,
                    event_type TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    body TEXT NOT NULL,
                    status TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(channel_id) REFERENCES notification_channels(channel_id),
                    FOREIGN KEY(task_id) REFERENCES monitor_tasks(task_id),
                    FOREIGN KEY(case_id) REFERENCES cases(case_id)
                );
                """
            )

    def seed_demo_data(self) -> None:
        with self.connect() as conn:
            count = conn.execute("SELECT COUNT(*) FROM cases").fetchone()[0]
            if count:
                return

            now = _now_iso()
            demo_cases = [
                CaseDetail(
                    case_id="case-zhzg-0001",
                    title="阿迪达斯变体商品页疑似仿冒",
                    brand_name="阿迪达斯",
                    suspect_name="阿波达斯",
                    platform="淘宝",
                    risk_score=92,
                    risk_level="high",
                    status=CaseStatus.open,
                    updated_at=datetime.now(timezone.utc),
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
                    updated_at=datetime.now(timezone.utc),
                    description="用于演示自动巡检、风险预警和文书辅助的样例案件。",
                    evidence_count=1,
                    template_count=1,
                    tags=["官网", "巡检", "预警"],
                    monitoring_scope=["official-site.example.com"],
                ),
            ]
            for case in demo_cases:
                conn.execute(
                    """
                    INSERT INTO cases (
                        case_id, title, brand_name, suspect_name, platform,
                        risk_score, risk_level, status, updated_at, description,
                        evidence_count, template_count, tags_json, monitoring_scope_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case.case_id,
                        case.title,
                        case.brand_name,
                        case.suspect_name,
                        case.platform,
                        case.risk_score,
                        case.risk_level,
                        case.status.value,
                        now,
                        case.description,
                        case.evidence_count,
                        case.template_count,
                        json.dumps(case.tags, ensure_ascii=False),
                        json.dumps(case.monitoring_scope, ensure_ascii=False),
                    ),
                )

            demo_drafts = [
                DocumentDraftRecord(
                    draft_id="draft-0001",
                    case_id="case-zhzg-0001",
                    template_key="lawyer-letter",
                    title="阿迪达斯变体商品页疑似仿冒 - 律师函初稿",
                    status=DraftStatus.generated,
                    content="## 律师函初稿\n\n现就相关页面中的疑似侵权展示提出说明与整改要求。",
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            ]
            for draft in demo_drafts:
                conn.execute(
                    """
                    INSERT INTO document_drafts (
                        draft_id, case_id, template_key, title, status, content,
                        created_at, updated_at, review_comment, export_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        draft.draft_id,
                        draft.case_id,
                        draft.template_key,
                        draft.title,
                        draft.status.value,
                        draft.content,
                        draft.created_at.isoformat(),
                        draft.updated_at.isoformat(),
                        draft.review_comment,
                        draft.export_path,
                    ),
                )

            demo_monitor_tasks = [
                MonitorTaskRecord(
                    task_id="monitor-0001",
                    name="阿迪达斯商品页巡检",
                    target_url="https://example.com/brand/adidas",
                    target_type="page",
                    site="品牌官网",
                    brand_keywords=["阿迪达斯", "阿波达斯"],
                    frequency_minutes=120,
                    risk_threshold=75,
                    status=MonitorTaskStatus.active,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    last_run_at=None,
                )
            ]
            for task in demo_monitor_tasks:
                conn.execute(
                    """
                    INSERT INTO monitor_tasks (
                        task_id, name, target_url, target_type, site,
                        brand_keywords_json, frequency_minutes, risk_threshold,
                        status, created_at, updated_at, last_run_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.task_id,
                        task.name,
                        task.target_url,
                        task.target_type,
                        task.site,
                        json.dumps(task.brand_keywords, ensure_ascii=False),
                        task.frequency_minutes,
                        task.risk_threshold,
                        task.status.value,
                        task.created_at.isoformat(),
                        task.updated_at.isoformat(),
                        None,
                    ),
                )

            demo_channels = [
                NotificationChannelRecord(
                    channel_id="channel-0001",
                    channel_type="email",
                    name="默认邮箱接收",
                    target="legal@example.com",
                    enabled=True,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
            ]
            for channel in demo_channels:
                conn.execute(
                    """
                    INSERT INTO notification_channels (
                        channel_id, channel_type, name, target, enabled, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        channel.channel_id,
                        channel.channel_type.value,
                        channel.name,
                        channel.target,
                        1 if channel.enabled else 0,
                        channel.created_at.isoformat(),
                        channel.updated_at.isoformat(),
                    ),
                )

    def _row_to_case_detail(self, row: sqlite3.Row) -> CaseDetail:
        return CaseDetail(
            case_id=row["case_id"],
            title=row["title"],
            brand_name=row["brand_name"],
            suspect_name=row["suspect_name"],
            platform=row["platform"],
            risk_score=row["risk_score"],
            risk_level=row["risk_level"],
            status=CaseStatus(row["status"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            description=row["description"],
            evidence_count=row["evidence_count"],
            template_count=row["template_count"],
            tags=json.loads(row["tags_json"]),
            monitoring_scope=json.loads(row["monitoring_scope_json"]),
        )

    def _row_to_case_summary(self, row: sqlite3.Row) -> CaseSummary:
        return CaseSummary(
            case_id=row["case_id"],
            title=row["title"],
            brand_name=row["brand_name"],
            suspect_name=row["suspect_name"],
            platform=row["platform"],
            risk_score=row["risk_score"],
            risk_level=row["risk_level"],
            status=CaseStatus(row["status"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_evidence(self, row: sqlite3.Row) -> EvidencePackRecord:
        return EvidencePackRecord(
            evidence_pack_id=row["evidence_pack_id"],
            case_id=row["case_id"],
            source_url=row["source_url"],
            source_title=row["source_title"],
            capture_channel=row["capture_channel"],
            note=row["note"],
            hash_sha256=row["hash_sha256"],
            snapshot_path=row["snapshot_path"],
            html_path=row["html_path"],
            created_at=datetime.fromisoformat(row["created_at"]),
            status=row["status"],
        )

    def _row_to_draft(self, row: sqlite3.Row) -> DocumentDraftRecord:
        return DocumentDraftRecord(
            draft_id=row["draft_id"],
            case_id=row["case_id"],
            template_key=row["template_key"],
            title=row["title"],
            status=DraftStatus(row["status"]),
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            review_comment=row["review_comment"],
            export_path=row["export_path"],
        )

    def _row_to_monitor_task(self, row: sqlite3.Row) -> MonitorTaskRecord:
        return MonitorTaskRecord(
            task_id=row["task_id"],
            name=row["name"],
            target_url=row["target_url"],
            target_type=row["target_type"],
            site=row["site"],
            brand_keywords=json.loads(row["brand_keywords_json"]),
            frequency_minutes=row["frequency_minutes"],
            risk_threshold=row["risk_threshold"],
            status=MonitorTaskStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_run_at=datetime.fromisoformat(row["last_run_at"]) if row["last_run_at"] else None,
        )

    def _row_to_notification_channel(self, row: sqlite3.Row) -> NotificationChannelRecord:
        return NotificationChannelRecord(
            channel_id=row["channel_id"],
            channel_type=row["channel_type"],
            name=row["name"],
            target=row["target"],
            enabled=bool(row["enabled"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def create_case(self, payload: CaseCreateRequest) -> CaseDetail:
        now = datetime.now(timezone.utc)
        serial = self._next_case_serial()
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
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO cases (
                    case_id, title, brand_name, suspect_name, platform,
                    risk_score, risk_level, status, updated_at, description,
                    evidence_count, template_count, tags_json, monitoring_scope_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.case_id,
                    record.title,
                    record.brand_name,
                    record.suspect_name,
                    record.platform,
                    record.risk_score,
                    record.risk_level,
                    record.status.value,
                    record.updated_at.isoformat(),
                    record.description,
                    record.evidence_count,
                    record.template_count,
                    json.dumps(record.tags, ensure_ascii=False),
                    json.dumps(record.monitoring_scope, ensure_ascii=False),
                ),
            )
        return record

    def list_cases(
        self,
        *,
        status: CaseStatus | None = None,
        platform: str | None = None,
        limit: int = 20,
    ) -> tuple[list[CaseSummary], int]:
        clauses = []
        params: list[str | int] = []
        if status is not None:
            clauses.append("status = ?")
            params.append(status.value)
        if platform is not None:
            clauses.append("platform = ?")
            params.append(platform)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            total = conn.execute(f"SELECT COUNT(*) FROM cases {where}", params).fetchone()[0]
            rows = conn.execute(
                f"""
                SELECT * FROM cases
                {where}
                ORDER BY updated_at DESC, case_id DESC
                LIMIT ?
                """,
                [*params, limit],
            ).fetchall()
        return [self._row_to_case_summary(row) for row in rows], total

    def get_case(self, case_id: str) -> CaseDetail | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        if row is None:
            return None
        return self._row_to_case_detail(row)

    def attach_evidence(self, case_id: str) -> CaseDetail | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
            if row is None:
                return None
            next_count = row["evidence_count"] + 1
            updated_at = _now_iso()
            conn.execute(
                "UPDATE cases SET evidence_count = ?, updated_at = ? WHERE case_id = ?",
                (next_count, updated_at, case_id),
            )
            row = conn.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,)).fetchone()
        return self._row_to_case_detail(row) if row else None

    def create_evidence_pack(self, payload: EvidencePackCreateRequest) -> EvidencePackRecord:
        created_at = datetime.now(timezone.utc)
        serial = self._next_evidence_serial()
        source_fingerprint = f"{payload.case_id}|{payload.source_url}|{payload.source_title}|{created_at.isoformat()}"
        digest = sha256(source_fingerprint.encode("utf-8")).hexdigest()
        record = EvidencePackRecord(
            evidence_pack_id=f"ep-{serial:04d}",
            case_id=payload.case_id,
            source_url=str(payload.source_url),
            source_title=payload.source_title,
            capture_channel=payload.capture_channel,
            note=payload.note,
            hash_sha256=digest,
            snapshot_path=f"evidence/{payload.case_id}/snapshot-{serial:04d}.png",
            html_path=f"evidence/{payload.case_id}/page-{serial:04d}.html",
            created_at=created_at,
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO evidence_packs (
                    evidence_pack_id, case_id, source_url, source_title,
                    capture_channel, note, hash_sha256, snapshot_path,
                    html_path, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.evidence_pack_id,
                    record.case_id,
                    record.source_url,
                    record.source_title,
                    record.capture_channel,
                    record.note,
                    record.hash_sha256,
                    record.snapshot_path,
                    record.html_path,
                    record.created_at.isoformat(),
                    record.status,
                ),
            )
        return record

    def list_evidence_packs(self, case_id: str | None = None) -> list[EvidencePackRecord]:
        if case_id is None:
            query = "SELECT * FROM evidence_packs ORDER BY created_at DESC, evidence_pack_id DESC"
            params: tuple[str, ...] = ()
        else:
            query = "SELECT * FROM evidence_packs WHERE case_id = ? ORDER BY created_at DESC, evidence_pack_id DESC"
            params = (case_id,)
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_evidence(row) for row in rows]

    def get_evidence_pack(self, evidence_pack_id: str) -> EvidencePackRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM evidence_packs WHERE evidence_pack_id = ?",
                (evidence_pack_id,),
            ).fetchone()
        return self._row_to_evidence(row) if row else None

    def create_document_draft(
        self,
        *,
        case_id: str,
        template_key: str,
        title: str,
        content: str,
    ) -> DocumentDraftRecord:
        created_at = datetime.now(timezone.utc)
        serial = self._next_draft_serial()
        record = DocumentDraftRecord(
            draft_id=f"draft-{serial:04d}",
            case_id=case_id,
            template_key=template_key,
            title=title,
            status=DraftStatus.generated,
            content=content,
            created_at=created_at,
            updated_at=created_at,
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO document_drafts (
                    draft_id, case_id, template_key, title, status, content,
                    created_at, updated_at, review_comment, export_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.draft_id,
                    record.case_id,
                    record.template_key,
                    record.title,
                    record.status.value,
                    record.content,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                    record.review_comment,
                    record.export_path,
                ),
            )
            conn.execute(
                """
                UPDATE cases
                SET template_count = template_count + 1,
                    status = ?,
                    updated_at = ?
                WHERE case_id = ?
                """,
                (CaseStatus.drafting.value, record.updated_at.isoformat(), case_id),
            )
        return record

    def list_document_drafts(self, case_id: str | None = None) -> list[DocumentDraftRecord]:
        if case_id:
            query = "SELECT * FROM document_drafts WHERE case_id = ? ORDER BY updated_at DESC, draft_id DESC"
            params: tuple[str, ...] = (case_id,)
        else:
            query = "SELECT * FROM document_drafts ORDER BY updated_at DESC, draft_id DESC"
            params = ()
        with self.connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_draft(row) for row in rows]

    def get_document_draft(self, draft_id: str) -> DocumentDraftRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM document_drafts WHERE draft_id = ?",
                (draft_id,),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def update_document_draft_review(
        self,
        *,
        draft_id: str,
        status: DraftStatus,
        review_comment: str,
    ) -> DocumentDraftRecord | None:
        updated_at = _now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE document_drafts
                SET status = ?, review_comment = ?, updated_at = ?
                WHERE draft_id = ?
                """,
                (status.value, review_comment, updated_at, draft_id),
            )
            row = conn.execute(
                "SELECT * FROM document_drafts WHERE draft_id = ?",
                (draft_id,),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def set_document_draft_export_path(self, draft_id: str, export_path: str) -> DocumentDraftRecord | None:
        updated_at = _now_iso()
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE document_drafts
                SET status = ?, export_path = ?, updated_at = ?
                WHERE draft_id = ?
                """,
                (DraftStatus.exported.value, export_path, updated_at, draft_id),
                )
            row = conn.execute(
                "SELECT * FROM document_drafts WHERE draft_id = ?",
                (draft_id,),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def create_monitor_task(self, payload: MonitorTaskCreateRequest) -> MonitorTaskRecord:
        created_at = datetime.now(timezone.utc)
        serial = self._next_monitor_task_serial()
        record = MonitorTaskRecord(
            task_id=f"monitor-{serial:04d}",
            name=payload.name,
            target_url=str(payload.target_url),
            target_type=payload.target_type,
            site=payload.site,
            brand_keywords=list(payload.brand_keywords),
            frequency_minutes=payload.frequency_minutes,
            risk_threshold=payload.risk_threshold,
            status=MonitorTaskStatus.active,
            created_at=created_at,
            updated_at=created_at,
            last_run_at=None,
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO monitor_tasks (
                    task_id, name, target_url, target_type, site,
                    brand_keywords_json, frequency_minutes, risk_threshold,
                    status, created_at, updated_at, last_run_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.task_id,
                    record.name,
                    record.target_url,
                    record.target_type,
                    record.site,
                    json.dumps(record.brand_keywords, ensure_ascii=False),
                    record.frequency_minutes,
                    record.risk_threshold,
                    record.status.value,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                    None,
                ),
            )
        return record

    def list_monitor_tasks(self) -> list[MonitorTaskRecord]:
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM monitor_tasks ORDER BY updated_at DESC, task_id DESC").fetchall()
        return [self._row_to_monitor_task(row) for row in rows]

    def get_monitor_task(self, task_id: str) -> MonitorTaskRecord | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM monitor_tasks WHERE task_id = ?", (task_id,)).fetchone()
        return self._row_to_monitor_task(row) if row else None

    def toggle_monitor_task(self, task_id: str, enabled: bool) -> MonitorTaskRecord | None:
        updated_at = _now_iso()
        status = MonitorTaskStatus.active.value if enabled else MonitorTaskStatus.paused.value
        with self.connect() as conn:
            conn.execute(
                "UPDATE monitor_tasks SET status = ?, updated_at = ? WHERE task_id = ?",
                (status, updated_at, task_id),
            )
            row = conn.execute("SELECT * FROM monitor_tasks WHERE task_id = ?", (task_id,)).fetchone()
        return self._row_to_monitor_task(row) if row else None

    def mark_monitor_task_run(self, task_id: str) -> MonitorTaskRecord | None:
        timestamp = _now_iso()
        with self.connect() as conn:
            conn.execute(
                "UPDATE monitor_tasks SET last_run_at = ?, updated_at = ? WHERE task_id = ?",
                (timestamp, timestamp, task_id),
            )
            row = conn.execute("SELECT * FROM monitor_tasks WHERE task_id = ?", (task_id,)).fetchone()
        return self._row_to_monitor_task(row) if row else None

    def create_notification_channel(self, payload: NotificationChannelCreateRequest) -> NotificationChannelRecord:
        created_at = datetime.now(timezone.utc)
        serial = self._next_notification_channel_serial()
        record = NotificationChannelRecord(
            channel_id=f"channel-{serial:04d}",
            channel_type=payload.channel_type,
            name=payload.name,
            target=payload.target,
            enabled=payload.enabled,
            created_at=created_at,
            updated_at=created_at,
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO notification_channels (
                    channel_id, channel_type, name, target, enabled, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.channel_id,
                    record.channel_type.value,
                    record.name,
                    record.target,
                    1 if record.enabled else 0,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                ),
            )
        return record

    def list_notification_channels(self) -> list[NotificationChannelRecord]:
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM notification_channels ORDER BY updated_at DESC, channel_id DESC"
            ).fetchall()
        return [self._row_to_notification_channel(row) for row in rows]

    def get_notification_channel(self, channel_id: str) -> NotificationChannelRecord | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM notification_channels WHERE channel_id = ?",
                (channel_id,),
            ).fetchone()
        return self._row_to_notification_channel(row) if row else None

    def create_notification_log(
        self,
        *,
        channel_id: str,
        event_type: str,
        subject: str,
        body: str,
        status: str,
        detail: str,
        task_id: str | None = None,
        case_id: str | None = None,
    ) -> str:
        created_at = _now_iso()
        serial = self._next_notification_log_serial()
        log_id = f"notify-log-{serial:04d}"
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO notification_logs (
                    log_id, channel_id, task_id, case_id, event_type,
                    subject, body, status, detail, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    channel_id,
                    task_id,
                    case_id,
                    event_type,
                    subject,
                    body,
                    status,
                    detail,
                    created_at,
                ),
            )
        return log_id

    def list_notification_logs(self, *, limit: int = 50) -> list[sqlite3.Row]:
        with self.connect() as conn:
            return conn.execute(
                """
                SELECT * FROM notification_logs
                ORDER BY created_at DESC, log_id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

    def _next_case_serial(self) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(case_id, 13) AS INTEGER)), 2) FROM cases"
            ).fetchone()
        return int(row[0]) + 1

    def _next_evidence_serial(self) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(evidence_pack_id, 4) AS INTEGER)), 0) FROM evidence_packs"
            ).fetchone()
        return int(row[0]) + 1

    def _next_draft_serial(self) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(draft_id, 7) AS INTEGER)), 0) FROM document_drafts"
            ).fetchone()
        return int(row[0]) + 1

    def _next_monitor_task_serial(self) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(task_id, 9) AS INTEGER)), 0) FROM monitor_tasks"
            ).fetchone()
        return int(row[0]) + 1

    def _next_notification_channel_serial(self) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(channel_id, 9) AS INTEGER)), 0) FROM notification_channels"
            ).fetchone()
        return int(row[0]) + 1

    def _next_notification_log_serial(self) -> int:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(log_id, 12) AS INTEGER)), 0) FROM notification_logs"
            ).fetchone()
        return int(row[0]) + 1
