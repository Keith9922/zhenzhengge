from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from app.core.storage import SQLiteStorage


class AuditService:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def log(
        self,
        *,
        actor_token: str,
        actor_user_id: str = "system",
        actor_org_id: str = "org-default",
        actor_role: str,
        action: str,
        resource_type: str,
        resource_id: str = "",
        request_id: str = "",
        payload: Mapping[str, Any] | None = None,
    ) -> str:
        payload_text = json.dumps(dict(payload or {}), ensure_ascii=False, default=str)
        return self.storage.create_audit_log(
            actor_token=actor_token,
            actor_user_id=actor_user_id,
            actor_org_id=actor_org_id,
            actor_role=actor_role,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            request_id=request_id,
            payload_json=payload_text,
        )
