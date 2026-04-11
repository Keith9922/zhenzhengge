from datetime import datetime, timezone
from hashlib import sha256
from itertools import count

from app.schemas.evidence import EvidencePackCreateRequest, EvidencePackRecord


_EVIDENCE_PACKS: list[EvidencePackRecord] = []
_EVIDENCE_COUNTER = count(1)


class EvidenceService:
    def __init__(self) -> None:
        self._items = _EVIDENCE_PACKS
        self._counter = _EVIDENCE_COUNTER

    def create_pack(self, payload: EvidencePackCreateRequest) -> EvidencePackRecord:
        created_at = datetime.now(timezone.utc)
        serial = next(self._counter)
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
        self._items.append(record)
        return record

    def list_packs(self, case_id: str | None = None) -> list[EvidencePackRecord]:
        if case_id is None:
            return list(self._items)
        return [item for item in self._items if item.case_id == case_id]
