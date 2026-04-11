from app.core.storage import SQLiteStorage
from app.schemas.monitoring import MonitorTaskCreateRequest, MonitorTaskRecord


class MonitorTaskService:
    def __init__(self, storage: SQLiteStorage) -> None:
        self.storage = storage

    def list_tasks(self) -> list[MonitorTaskRecord]:
        return self.storage.list_monitor_tasks()

    def get_task(self, task_id: str) -> MonitorTaskRecord | None:
        return self.storage.get_monitor_task(task_id)

    def create_task(self, payload: MonitorTaskCreateRequest) -> MonitorTaskRecord:
        return self.storage.create_monitor_task(payload)

    def toggle_task(self, task_id: str, enabled: bool) -> MonitorTaskRecord | None:
        return self.storage.toggle_monitor_task(task_id, enabled)

    def mark_run(self, task_id: str) -> MonitorTaskRecord | None:
        return self.storage.mark_monitor_task_run(task_id)
