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
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    owner_user_id TEXT NOT NULL DEFAULT 'system',
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
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    owner_user_id TEXT NOT NULL DEFAULT 'system',
                    source_url TEXT NOT NULL,
                    source_title TEXT NOT NULL,
                    capture_channel TEXT NOT NULL,
                    note TEXT,
                    hash_sha256 TEXT NOT NULL,
                    html_sha256 TEXT NOT NULL DEFAULT '',
                    screenshot_sha256 TEXT NOT NULL DEFAULT '',
                    chain_sha256 TEXT NOT NULL DEFAULT '',
                    snapshot_path TEXT NOT NULL,
                    html_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    timestamp_status TEXT NOT NULL DEFAULT 'not_configured',
                    timestamp_provider TEXT NOT NULL DEFAULT '',
                    timestamp_token_path TEXT NOT NULL DEFAULT '',
                    timestamp_message TEXT NOT NULL DEFAULT '',
                    timestamp_at TEXT,
                    FOREIGN KEY(case_id) REFERENCES cases(case_id)
                );

                CREATE TABLE IF NOT EXISTS document_drafts (
                    draft_id TEXT PRIMARY KEY,
                    case_id TEXT NOT NULL,
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    owner_user_id TEXT NOT NULL DEFAULT 'system',
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
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    owner_user_id TEXT NOT NULL DEFAULT 'system',
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
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    owner_user_id TEXT NOT NULL DEFAULT 'system',
                    channel_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    target TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notification_logs (
                    log_id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
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

                CREATE TABLE IF NOT EXISTS monitor_runs (
                    run_id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    task_id TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    finished_at TEXT,
                    status TEXT NOT NULL,
                    risk_score INTEGER NOT NULL DEFAULT 0,
                    case_id TEXT,
                    evidence_pack_id TEXT,
                    detail TEXT NOT NULL DEFAULT '',
                    FOREIGN KEY(task_id) REFERENCES monitor_tasks(task_id),
                    FOREIGN KEY(case_id) REFERENCES cases(case_id),
                    FOREIGN KEY(evidence_pack_id) REFERENCES evidence_packs(evidence_pack_id)
                );

                CREATE TABLE IF NOT EXISTS audit_logs (
                    audit_id TEXT PRIMARY KEY,
                    actor_token TEXT NOT NULL,
                    actor_user_id TEXT NOT NULL DEFAULT 'system',
                    actor_org_id TEXT NOT NULL DEFAULT 'org-default',
                    actor_role TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource_type TEXT NOT NULL,
                    resource_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS brand_profiles (
                    profile_id TEXT PRIMARY KEY,
                    organization_id TEXT NOT NULL DEFAULT 'org-default',
                    owner_user_id TEXT NOT NULL DEFAULT 'system',
                    brand_name TEXT NOT NULL,
                    trademark_classes_json TEXT NOT NULL DEFAULT '[]',
                    trademark_numbers_json TEXT NOT NULL DEFAULT '[]',
                    confusable_terms_json TEXT NOT NULL DEFAULT '[]',
                    protection_keywords_json TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                """
            )
            self._ensure_column(conn, "evidence_packs", "html_sha256", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "evidence_packs", "screenshot_sha256", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "evidence_packs", "chain_sha256", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "evidence_packs", "timestamp_status", "TEXT NOT NULL DEFAULT 'not_configured'")
            self._ensure_column(conn, "evidence_packs", "timestamp_provider", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "evidence_packs", "timestamp_token_path", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "evidence_packs", "timestamp_message", "TEXT NOT NULL DEFAULT ''")
            self._ensure_column(conn, "evidence_packs", "timestamp_at", "TEXT")
            self._ensure_column(conn, "cases", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'")
            self._ensure_column(conn, "cases", "owner_user_id", "TEXT NOT NULL DEFAULT 'system'")
            self._ensure_column(conn, "evidence_packs", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'")
            self._ensure_column(conn, "evidence_packs", "owner_user_id", "TEXT NOT NULL DEFAULT 'system'")
            self._ensure_column(conn, "document_drafts", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'")
            self._ensure_column(conn, "document_drafts", "owner_user_id", "TEXT NOT NULL DEFAULT 'system'")
            self._ensure_column(conn, "monitor_tasks", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'")
            self._ensure_column(conn, "monitor_tasks", "owner_user_id", "TEXT NOT NULL DEFAULT 'system'")
            self._ensure_column(
                conn, "notification_channels", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'"
            )
            self._ensure_column(conn, "notification_channels", "owner_user_id", "TEXT NOT NULL DEFAULT 'system'")
            self._ensure_column(conn, "notification_logs", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'")
            self._ensure_column(conn, "monitor_runs", "organization_id", "TEXT NOT NULL DEFAULT 'org-default'")
            self._ensure_column(conn, "audit_logs", "actor_user_id", "TEXT NOT NULL DEFAULT 'system'")
            self._ensure_column(conn, "audit_logs", "actor_org_id", "TEXT NOT NULL DEFAULT 'org-default'")

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
                        case_id, organization_id, owner_user_id, title, brand_name, suspect_name, platform,
                        risk_score, risk_level, status, updated_at, description,
                        evidence_count, template_count, tags_json, monitoring_scope_json
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        case.case_id,
                        "org-default",
                        "system",
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
                        draft_id, case_id, organization_id, owner_user_id, template_key, title, status, content,
                        created_at, updated_at, review_comment, export_path
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        draft.draft_id,
                        draft.case_id,
                        "org-default",
                        "system",
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
                        task_id, organization_id, owner_user_id, name, target_url, target_type, site,
                        brand_keywords_json, frequency_minutes, risk_threshold,
                        status, created_at, updated_at, last_run_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        task.task_id,
                        "org-default",
                        "system",
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
                        channel_id, organization_id, owner_user_id, channel_type, name, target, enabled, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        channel.channel_id,
                        "org-default",
                        "system",
                        channel.channel_type.value,
                        channel.name,
                        channel.target,
                        1 if channel.enabled else 0,
                        channel.created_at.isoformat(),
                        channel.updated_at.isoformat(),
                    ),
                )

    @staticmethod
    def _ensure_column(conn: sqlite3.Connection, table: str, column: str, definition: str) -> None:
        rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
        existing = {row[1] for row in rows}
        if column in existing:
            return
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")

    def _row_to_case_detail(self, row: sqlite3.Row) -> CaseDetail:
        return CaseDetail(
            case_id=row["case_id"],
            organization_id=row["organization_id"],
            owner_user_id=row["owner_user_id"],
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
            organization_id=row["organization_id"],
            owner_user_id=row["owner_user_id"],
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
        keys = set(row.keys())
        return EvidencePackRecord(
            evidence_pack_id=row["evidence_pack_id"],
            case_id=row["case_id"],
            organization_id=row["organization_id"] if "organization_id" in keys else "org-default",
            owner_user_id=row["owner_user_id"] if "owner_user_id" in keys else "system",
            source_url=row["source_url"],
            source_title=row["source_title"],
            capture_channel=row["capture_channel"],
            note=row["note"],
            hash_sha256=row["hash_sha256"],
            html_sha256=row["html_sha256"] if "html_sha256" in keys else "",
            screenshot_sha256=row["screenshot_sha256"] if "screenshot_sha256" in keys else "",
            chain_sha256=row["chain_sha256"] if "chain_sha256" in keys else "",
            snapshot_path=row["snapshot_path"],
            html_path=row["html_path"],
            created_at=datetime.fromisoformat(row["created_at"]),
            status=row["status"],
            timestamp_status=row["timestamp_status"] if "timestamp_status" in keys else "not_configured",
            timestamp_provider=row["timestamp_provider"] if "timestamp_provider" in keys else "",
            timestamp_token_path=row["timestamp_token_path"] if "timestamp_token_path" in keys else "",
            timestamp_message=row["timestamp_message"] if "timestamp_message" in keys else "",
            timestamp_at=row["timestamp_at"] if "timestamp_at" in keys else None,
        )

    def _row_to_draft(self, row: sqlite3.Row) -> DocumentDraftRecord:
        return DocumentDraftRecord(
            draft_id=row["draft_id"],
            case_id=row["case_id"],
            organization_id=row["organization_id"],
            owner_user_id=row["owner_user_id"],
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
            organization_id=row["organization_id"],
            owner_user_id=row["owner_user_id"],
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
            organization_id=row["organization_id"],
            owner_user_id=row["owner_user_id"],
            channel_type=row["channel_type"],
            name=row["name"],
            target=row["target"],
            enabled=bool(row["enabled"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    @staticmethod
    def _append_org_clause(
        clauses: list[str],
        params: list[str | int],
        *,
        organization_id: str | None,
        field_name: str = "organization_id",
    ) -> None:
        if organization_id:
            clauses.append(f"{field_name} = ?")
            params.append(organization_id)

    def create_case(
        self,
        payload: CaseCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> CaseDetail:
        now = datetime.now(timezone.utc)
        with self.connect() as conn:
            serial = self._next_case_serial(conn)
            record = CaseDetail(
                case_id=f"case-zhzg-{serial:04d}",
                organization_id=organization_id,
                owner_user_id=owner_user_id,
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
            conn.execute(
                """
                INSERT INTO cases (
                    case_id, organization_id, owner_user_id, title, brand_name, suspect_name, platform,
                    risk_score, risk_level, status, updated_at, description,
                    evidence_count, template_count, tags_json, monitoring_scope_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.case_id,
                    record.organization_id,
                    record.owner_user_id,
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
        organization_id: str | None = None,
        limit: int = 20,
    ) -> tuple[list[CaseSummary], int]:
        clauses = []
        params: list[str | int] = []
        self._append_org_clause(clauses, params, organization_id=organization_id)
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

    def get_case(self, case_id: str, *, organization_id: str | None = None) -> CaseDetail | None:
        clauses = ["case_id = ?"]
        params: list[str] = [case_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            row = conn.execute(f"SELECT * FROM cases WHERE {where}", tuple(params)).fetchone()
        if row is None:
            return None
        return self._row_to_case_detail(row)

    def update_case_description(
        self, case_id: str, description: str, *, organization_id: str | None = None
    ) -> CaseDetail | None:
        clauses = ["case_id = ?"]
        params: list[str] = [case_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        updated_at = _now_iso()
        with self.connect() as conn:
            conn.execute(
                f"UPDATE cases SET description = ?, updated_at = ? WHERE {where}",
                (description, updated_at, *params),
            )
            row = conn.execute(f"SELECT * FROM cases WHERE {where}", tuple(params)).fetchone()
        return self._row_to_case_detail(row) if row else None

    def attach_evidence(self, case_id: str, *, organization_id: str | None = None) -> CaseDetail | None:
        clauses = ["case_id = ?"]
        params: list[str] = [case_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            row = conn.execute(f"SELECT * FROM cases WHERE {where}", tuple(params)).fetchone()
            if row is None:
                return None
            next_count = row["evidence_count"] + 1
            updated_at = _now_iso()
            conn.execute(
                f"UPDATE cases SET evidence_count = ?, updated_at = ? WHERE {where}",
                (next_count, updated_at, *params),
            )
            row = conn.execute(f"SELECT * FROM cases WHERE {where}", tuple(params)).fetchone()
        return self._row_to_case_detail(row) if row else None

    def create_evidence_pack(
        self,
        payload: EvidencePackCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> EvidencePackRecord:
        created_at = datetime.now(timezone.utc)
        with self.connect() as conn:
            serial = self._next_evidence_serial(conn)
            source_fingerprint = f"{payload.case_id}|{payload.source_url}|{payload.source_title}|{created_at.isoformat()}"
            digest = sha256(source_fingerprint.encode("utf-8")).hexdigest()
            record = EvidencePackRecord(
                evidence_pack_id=f"ep-{serial:04d}",
                case_id=payload.case_id,
                organization_id=organization_id,
                owner_user_id=owner_user_id,
                source_url=str(payload.source_url),
                source_title=payload.source_title,
                capture_channel=payload.capture_channel,
                note=payload.note,
                hash_sha256=digest,
                html_sha256="",
                screenshot_sha256="",
                chain_sha256=digest,
                snapshot_path=f"evidence/{payload.case_id}/snapshot-{serial:04d}.png",
                html_path=f"evidence/{payload.case_id}/page-{serial:04d}.html",
                created_at=created_at,
            )
            conn.execute(
                """
                INSERT INTO evidence_packs (
                    evidence_pack_id, case_id, organization_id, owner_user_id, source_url, source_title,
                    capture_channel, note, hash_sha256, html_sha256, screenshot_sha256, chain_sha256, snapshot_path,
                    html_path, created_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.evidence_pack_id,
                    record.case_id,
                    record.organization_id,
                    record.owner_user_id,
                    record.source_url,
                    record.source_title,
                    record.capture_channel,
                    record.note,
                    record.hash_sha256,
                    record.html_sha256,
                    record.screenshot_sha256,
                    record.chain_sha256,
                    record.snapshot_path,
                    record.html_path,
                    record.created_at.isoformat(),
                    record.status,
                ),
            )
        return record

    def list_evidence_packs(
        self,
        case_id: str | None = None,
        *,
        organization_id: str | None = None,
    ) -> list[EvidencePackRecord]:
        clauses: list[str] = []
        params: list[str] = []
        self._append_org_clause(clauses, params, organization_id=organization_id)
        if case_id is not None:
            clauses.append("case_id = ?")
            params.append(case_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM evidence_packs {where} ORDER BY created_at DESC, evidence_pack_id DESC"
        with self.connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._row_to_evidence(row) for row in rows]

    def get_evidence_pack(
        self, evidence_pack_id: str, *, organization_id: str | None = None
    ) -> EvidencePackRecord | None:
        clauses = ["evidence_pack_id = ?"]
        params: list[str] = [evidence_pack_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            row = conn.execute(
                f"SELECT * FROM evidence_packs WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_evidence(row) if row else None

    def create_document_draft(
        self,
        *,
        case_id: str,
        organization_id: str,
        owner_user_id: str,
        template_key: str,
        title: str,
        content: str,
    ) -> DocumentDraftRecord:
        created_at = datetime.now(timezone.utc)
        with self.connect() as conn:
            serial = self._next_draft_serial(conn)
            record = DocumentDraftRecord(
                draft_id=f"draft-{serial:04d}",
                case_id=case_id,
                organization_id=organization_id,
                owner_user_id=owner_user_id,
                template_key=template_key,
                title=title,
                status=DraftStatus.generated,
                content=content,
                created_at=created_at,
                updated_at=created_at,
            )
            conn.execute(
                """
                INSERT INTO document_drafts (
                    draft_id, case_id, organization_id, owner_user_id, template_key, title, status, content,
                    created_at, updated_at, review_comment, export_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.draft_id,
                    record.case_id,
                    record.organization_id,
                    record.owner_user_id,
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
                WHERE case_id = ? AND organization_id = ?
                """,
                (CaseStatus.drafting.value, record.updated_at.isoformat(), case_id, organization_id),
            )
        return record

    def list_document_drafts(
        self, case_id: str | None = None, *, organization_id: str | None = None
    ) -> list[DocumentDraftRecord]:
        clauses: list[str] = []
        params: list[str] = []
        self._append_org_clause(clauses, params, organization_id=organization_id)
        if case_id:
            clauses.append("case_id = ?")
            params.append(case_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM document_drafts {where} ORDER BY updated_at DESC, draft_id DESC"
        with self.connect() as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._row_to_draft(row) for row in rows]

    def get_document_draft(
        self, draft_id: str, *, organization_id: str | None = None
    ) -> DocumentDraftRecord | None:
        clauses = ["draft_id = ?"]
        params: list[str] = [draft_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            row = conn.execute(
                f"SELECT * FROM document_drafts WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def update_document_draft_review(
        self,
        *,
        draft_id: str,
        organization_id: str | None = None,
        status: DraftStatus,
        review_comment: str,
    ) -> DocumentDraftRecord | None:
        updated_at = _now_iso()
        clauses = ["draft_id = ?"]
        params: list[str] = [draft_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"""
                UPDATE document_drafts
                SET status = ?, review_comment = ?, updated_at = ?
                WHERE {where}
                """,
                (status.value, review_comment, updated_at, *params),
            )
            row = conn.execute(
                f"SELECT * FROM document_drafts WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def update_document_draft_content(
        self,
        *,
        draft_id: str,
        organization_id: str | None = None,
        content: str,
        title: str | None = None,
    ) -> DocumentDraftRecord | None:
        updated_at = _now_iso()
        clauses = ["draft_id = ?"]
        params: list[str] = [draft_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            if title is None:
                conn.execute(
                    f"""
                    UPDATE document_drafts
                    SET content = ?, updated_at = ?
                    WHERE {where}
                    """,
                    (content, updated_at, *params),
                )
            else:
                conn.execute(
                    f"""
                    UPDATE document_drafts
                    SET content = ?, title = ?, updated_at = ?
                    WHERE {where}
                    """,
                    (content, title, updated_at, *params),
                )
            row = conn.execute(
                f"SELECT * FROM document_drafts WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def set_document_draft_export_path(
        self, draft_id: str, export_path: str, *, organization_id: str | None = None
    ) -> DocumentDraftRecord | None:
        updated_at = _now_iso()
        clauses = ["draft_id = ?"]
        params: list[str] = [draft_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"""
                UPDATE document_drafts
                SET status = ?, export_path = ?, updated_at = ?
                WHERE {where}
                """,
                (DraftStatus.exported.value, export_path, updated_at, *params),
            )
            row = conn.execute(
                f"SELECT * FROM document_drafts WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_draft(row) if row else None

    def create_monitor_task(
        self,
        payload: MonitorTaskCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> MonitorTaskRecord:
        created_at = datetime.now(timezone.utc)
        with self.connect() as conn:
            serial = self._next_monitor_task_serial(conn)
            record = MonitorTaskRecord(
                task_id=f"monitor-{serial:04d}",
                organization_id=organization_id,
                owner_user_id=owner_user_id,
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
            conn.execute(
                """
                INSERT INTO monitor_tasks (
                    task_id, organization_id, owner_user_id, name, target_url, target_type, site,
                    brand_keywords_json, frequency_minutes, risk_threshold,
                    status, created_at, updated_at, last_run_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.task_id,
                    record.organization_id,
                    record.owner_user_id,
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

    def list_monitor_tasks(self, *, organization_id: str | None = None) -> list[MonitorTaskRecord]:
        clauses: list[str] = []
        params: list[str] = []
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM monitor_tasks {where} ORDER BY updated_at DESC, task_id DESC", tuple(params)
            ).fetchall()
        return [self._row_to_monitor_task(row) for row in rows]

    def get_monitor_task(self, task_id: str, *, organization_id: str | None = None) -> MonitorTaskRecord | None:
        clauses = ["task_id = ?"]
        params: list[str] = [task_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            row = conn.execute(f"SELECT * FROM monitor_tasks WHERE {where}", tuple(params)).fetchone()
        return self._row_to_monitor_task(row) if row else None

    def toggle_monitor_task(
        self, task_id: str, enabled: bool, *, organization_id: str | None = None
    ) -> MonitorTaskRecord | None:
        updated_at = _now_iso()
        status = MonitorTaskStatus.active.value if enabled else MonitorTaskStatus.paused.value
        clauses = ["task_id = ?"]
        params: list[str] = [task_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE monitor_tasks SET status = ?, updated_at = ? WHERE {where}",
                (status, updated_at, *params),
            )
            row = conn.execute(f"SELECT * FROM monitor_tasks WHERE {where}", tuple(params)).fetchone()
        return self._row_to_monitor_task(row) if row else None

    def mark_monitor_task_run(
        self, task_id: str, *, organization_id: str | None = None
    ) -> MonitorTaskRecord | None:
        timestamp = _now_iso()
        clauses = ["task_id = ?"]
        params: list[str] = [task_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE monitor_tasks SET last_run_at = ?, updated_at = ? WHERE {where}",
                (timestamp, timestamp, *params),
            )
            row = conn.execute(f"SELECT * FROM monitor_tasks WHERE {where}", tuple(params)).fetchone()
        return self._row_to_monitor_task(row) if row else None

    def create_notification_channel(
        self,
        payload: NotificationChannelCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> NotificationChannelRecord:
        created_at = datetime.now(timezone.utc)
        with self.connect() as conn:
            serial = self._next_notification_channel_serial(conn)
            record = NotificationChannelRecord(
                channel_id=f"channel-{serial:04d}",
                organization_id=organization_id,
                owner_user_id=owner_user_id,
                channel_type=payload.channel_type,
                name=payload.name,
                target=payload.target,
                enabled=payload.enabled,
                created_at=created_at,
                updated_at=created_at,
            )
            conn.execute(
                """
                INSERT INTO notification_channels (
                    channel_id, organization_id, owner_user_id, channel_type, name, target, enabled, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.channel_id,
                    record.organization_id,
                    record.owner_user_id,
                    record.channel_type.value,
                    record.name,
                    record.target,
                    1 if record.enabled else 0,
                    record.created_at.isoformat(),
                    record.updated_at.isoformat(),
                ),
            )
        return record

    def list_notification_channels(self, *, organization_id: str | None = None) -> list[NotificationChannelRecord]:
        clauses: list[str] = []
        params: list[str] = []
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"SELECT * FROM notification_channels {where} ORDER BY updated_at DESC, channel_id DESC",
                tuple(params),
            ).fetchall()
        return [self._row_to_notification_channel(row) for row in rows]

    def get_notification_channel(
        self, channel_id: str, *, organization_id: str | None = None
    ) -> NotificationChannelRecord | None:
        clauses = ["channel_id = ?"]
        params: list[str] = [channel_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            row = conn.execute(
                f"SELECT * FROM notification_channels WHERE {where}",
                tuple(params),
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
        organization_id: str,
        task_id: str | None = None,
        case_id: str | None = None,
    ) -> str:
        created_at = _now_iso()
        with self.connect() as conn:
            serial = self._next_notification_log_serial(conn)
            log_id = f"notify-log-{serial:04d}"
            conn.execute(
                """
                INSERT INTO notification_logs (
                    log_id, organization_id, channel_id, task_id, case_id, event_type,
                    subject, body, status, detail, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    organization_id,
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

    def list_notification_logs(
        self, *, organization_id: str | None = None, limit: int = 50
    ) -> list[sqlite3.Row]:
        clauses: list[str] = []
        params: list[str | int] = []
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            return conn.execute(
                f"""
                SELECT * FROM notification_logs
                {where}
                ORDER BY created_at DESC, log_id DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()

    def update_evidence_hashes(
        self,
        *,
        evidence_pack_id: str,
        organization_id: str | None = None,
        hash_sha256: str,
        html_sha256: str,
        screenshot_sha256: str,
        chain_sha256: str,
    ) -> EvidencePackRecord | None:
        clauses = ["evidence_pack_id = ?"]
        params: list[str] = [evidence_pack_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"""
                UPDATE evidence_packs
                SET hash_sha256 = ?, html_sha256 = ?, screenshot_sha256 = ?, chain_sha256 = ?
                WHERE {where}
                """,
                (hash_sha256, html_sha256, screenshot_sha256, chain_sha256, *params),
            )
            row = conn.execute(
                f"SELECT * FROM evidence_packs WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_evidence(row) if row else None

    def update_evidence_timestamp(
        self,
        *,
        evidence_pack_id: str,
        organization_id: str | None = None,
        timestamp_status: str,
        timestamp_provider: str,
        timestamp_token_path: str,
        timestamp_message: str,
        timestamp_at: str | None,
    ) -> EvidencePackRecord | None:
        clauses = ["evidence_pack_id = ?"]
        params: list[str] = [evidence_pack_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"""
                UPDATE evidence_packs
                SET timestamp_status = ?, timestamp_provider = ?, timestamp_token_path = ?,
                    timestamp_message = ?, timestamp_at = ?
                WHERE {where}
                """,
                (
                    timestamp_status,
                    timestamp_provider,
                    timestamp_token_path,
                    timestamp_message,
                    timestamp_at,
                    *params,
                ),
            )
            row = conn.execute(
                f"SELECT * FROM evidence_packs WHERE {where}",
                tuple(params),
            ).fetchone()
        return self._row_to_evidence(row) if row else None

    def create_monitor_run(self, *, task_id: str, organization_id: str) -> str:
        started_at = _now_iso()
        with self.connect() as conn:
            run_id = f"run-{self._next_monitor_run_serial(conn):06d}"
            conn.execute(
                """
                INSERT INTO monitor_runs (run_id, organization_id, task_id, started_at, status, detail)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, organization_id, task_id, started_at, "running", ""),
            )
        return run_id

    def finish_monitor_run(
        self,
        *,
        run_id: str,
        organization_id: str | None = None,
        status: str,
        risk_score: int,
        detail: str,
        case_id: str | None = None,
        evidence_pack_id: str | None = None,
    ) -> None:
        finished_at = _now_iso()
        clauses = ["run_id = ?"]
        params: list[str] = [run_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            conn.execute(
                f"""
                UPDATE monitor_runs
                SET finished_at = ?, status = ?, risk_score = ?, case_id = ?, evidence_pack_id = ?, detail = ?
                WHERE {where}
                """,
                (finished_at, status, risk_score, case_id, evidence_pack_id, detail, *params),
            )

    def list_monitor_runs(
        self, *, task_id: str, organization_id: str | None = None, limit: int = 20
    ) -> list[sqlite3.Row]:
        clauses = ["task_id = ?"]
        params: list[str | int] = [task_id]
        self._append_org_clause(clauses, params, organization_id=organization_id)
        where = " AND ".join(clauses)
        with self.connect() as conn:
            return conn.execute(
                f"""
                SELECT * FROM monitor_runs
                WHERE {where}
                ORDER BY started_at DESC, run_id DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()

    def create_audit_log(
        self,
        *,
        actor_token: str,
        actor_user_id: str,
        actor_org_id: str,
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str,
        request_id: str,
        payload_json: str,
    ) -> str:
        with self.connect() as conn:
            audit_id = f"audit-{self._next_audit_serial(conn):06d}"
            conn.execute(
                """
                INSERT INTO audit_logs (
                    audit_id, actor_token, actor_user_id, actor_org_id, actor_role, action, resource_type,
                    resource_id, request_id, payload_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    audit_id,
                    actor_token,
                    actor_user_id,
                    actor_org_id,
                    actor_role,
                    action,
                    resource_type,
                    resource_id,
                    request_id,
                    payload_json,
                    _now_iso(),
                ),
            )
        return audit_id

    def list_audit_logs(self, *, actor_org_id: str | None = None, limit: int = 100) -> list[sqlite3.Row]:
        clauses: list[str] = []
        params: list[str | int] = []
        self._append_org_clause(clauses, params, organization_id=actor_org_id, field_name="actor_org_id")
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self.connect() as conn:
            return conn.execute(
                f"""
                SELECT * FROM audit_logs
                {where}
                ORDER BY created_at DESC, audit_id DESC
                LIMIT ?
                """,
                (*params, limit),
            ).fetchall()

    def _next_case_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(case_id, 13) AS INTEGER)), 2) FROM cases"
        ).fetchone()
        return int(row[0]) + 1

    def _next_evidence_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(evidence_pack_id, 4) AS INTEGER)), 0) FROM evidence_packs"
        ).fetchone()
        return int(row[0]) + 1

    def _next_draft_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(draft_id, 7) AS INTEGER)), 0) FROM document_drafts"
        ).fetchone()
        return int(row[0]) + 1

    def _next_monitor_task_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(task_id, 9) AS INTEGER)), 0) FROM monitor_tasks"
        ).fetchone()
        return int(row[0]) + 1

    def _next_notification_channel_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(channel_id, 9) AS INTEGER)), 0) FROM notification_channels"
        ).fetchone()
        return int(row[0]) + 1

    def _next_notification_log_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(log_id, 12) AS INTEGER)), 0) FROM notification_logs"
        ).fetchone()
        return int(row[0]) + 1

    # ------------------------------------------------------------------ #
    # brand_profiles                                                       #
    # ------------------------------------------------------------------ #

    def _row_to_brand_profile(self, row: sqlite3.Row) -> "BrandProfileRecord":
        from app.schemas.brand_profiles import BrandProfileRecord
        from datetime import datetime
        return BrandProfileRecord(
            profile_id=row["profile_id"],
            organization_id=row["organization_id"],
            owner_user_id=row["owner_user_id"],
            brand_name=row["brand_name"],
            trademark_classes=json.loads(row["trademark_classes_json"] or "[]"),
            trademark_numbers=json.loads(row["trademark_numbers_json"] or "[]"),
            confusable_terms=json.loads(row["confusable_terms_json"] or "[]"),
            protection_keywords=json.loads(row["protection_keywords_json"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def list_brand_profiles(self, *, organization_id: str | None = None) -> list["BrandProfileRecord"]:
        with self.connect() as conn:
            clauses: list[str] = []
            params: list = []
            self._append_org_clause(clauses, params, organization_id=organization_id)
            where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
            sql = f"SELECT * FROM brand_profiles{where} ORDER BY created_at DESC"
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_brand_profile(r) for r in rows]

    def get_brand_profile(self, profile_id: str, *, organization_id: str | None = None) -> "BrandProfileRecord | None":
        with self.connect() as conn:
            sql = "SELECT * FROM brand_profiles WHERE profile_id = ?"
            params: list = [profile_id]
            if organization_id:
                sql += " AND organization_id = ?"
                params.append(organization_id)
            row = conn.execute(sql, params).fetchone()
            return self._row_to_brand_profile(row) if row else None

    def create_brand_profile(
        self,
        payload: "BrandProfileCreateRequest",
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> "BrandProfileRecord":
        from app.schemas.brand_profiles import BrandProfileCreateRequest  # noqa: F401
        now = _now_iso()
        with self.connect() as conn:
            serial = conn.execute(
                "SELECT COALESCE(MAX(CAST(SUBSTR(profile_id, 9) AS INTEGER)), 0) FROM brand_profiles"
            ).fetchone()[0]
            profile_id = f"profile-{int(serial) + 1:04d}"
            conn.execute(
                """INSERT INTO brand_profiles
                   (profile_id, organization_id, owner_user_id, brand_name,
                    trademark_classes_json, trademark_numbers_json,
                    confusable_terms_json, protection_keywords_json,
                    created_at, updated_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (
                    profile_id, organization_id, owner_user_id, payload.brand_name,
                    json.dumps(payload.trademark_classes, ensure_ascii=False),
                    json.dumps(payload.trademark_numbers, ensure_ascii=False),
                    json.dumps(payload.confusable_terms, ensure_ascii=False),
                    json.dumps(payload.protection_keywords, ensure_ascii=False),
                    now, now,
                ),
            )
        return self.get_brand_profile(profile_id)  # type: ignore[return-value]

    def update_brand_profile(
        self,
        profile_id: str,
        payload: "BrandProfileUpdateRequest",
        *,
        organization_id: str | None = None,
    ) -> "BrandProfileRecord | None":
        existing = self.get_brand_profile(profile_id, organization_id=organization_id)
        if not existing:
            return None
        now = _now_iso()
        fields: list[str] = ["updated_at = ?"]
        params: list = [now]
        if payload.brand_name is not None:
            fields.append("brand_name = ?")
            params.append(payload.brand_name)
        if payload.trademark_classes is not None:
            fields.append("trademark_classes_json = ?")
            params.append(json.dumps(payload.trademark_classes, ensure_ascii=False))
        if payload.trademark_numbers is not None:
            fields.append("trademark_numbers_json = ?")
            params.append(json.dumps(payload.trademark_numbers, ensure_ascii=False))
        if payload.confusable_terms is not None:
            fields.append("confusable_terms_json = ?")
            params.append(json.dumps(payload.confusable_terms, ensure_ascii=False))
        if payload.protection_keywords is not None:
            fields.append("protection_keywords_json = ?")
            params.append(json.dumps(payload.protection_keywords, ensure_ascii=False))
        params.append(profile_id)
        with self.connect() as conn:
            conn.execute(
                f"UPDATE brand_profiles SET {', '.join(fields)} WHERE profile_id = ?",
                params,
            )
        return self.get_brand_profile(profile_id, organization_id=organization_id)

    def delete_brand_profile(self, profile_id: str, *, organization_id: str | None = None) -> bool:
        existing = self.get_brand_profile(profile_id, organization_id=organization_id)
        if not existing:
            return False
        with self.connect() as conn:
            conn.execute("DELETE FROM brand_profiles WHERE profile_id = ?", (profile_id,))
        return True

    def _next_monitor_run_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(run_id, 5) AS INTEGER)), 0) FROM monitor_runs"
        ).fetchone()
        return int(row[0]) + 1

    def _next_audit_serial(self, conn: sqlite3.Connection) -> int:
        row = conn.execute(
            "SELECT COALESCE(MAX(CAST(SUBSTR(audit_id, 7) AS INTEGER)), 0) FROM audit_logs"
        ).fetchone()
        return int(row[0]) + 1
