from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from app.schemas.cases import CaseCreateRequest, CaseDetail, CaseStatus, CaseSummary
from app.schemas.evidence import EvidencePackCreateRequest, EvidencePackRecord


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

    def __post_init__(self) -> None:
        self.db_path = _parse_sqlite_path(self.db_url)
        if self.db_path != ":memory:":
            path_obj = Path(self.db_path)
            if path_obj.parent and str(path_obj.parent) not in {"", "."}:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
        self.ensure_schema()
        self.seed_demo_data()

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
