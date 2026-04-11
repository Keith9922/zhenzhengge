from dataclasses import dataclass


@dataclass(slots=True)
class WorkflowResult:
    workflow_name: str
    status: str
    detail: str


class HermesOrchestrator:
    def __init__(self) -> None:
        self._status = "stub"

    def health(self) -> dict[str, str]:
        return {
            "name": "hermes_orchestrator",
            "status": self._status,
            "description": "后端工作流编排中枢预留位",
        }

    def submit_capture_workflow(self, case_id: str) -> WorkflowResult:
        return WorkflowResult(
            workflow_name="capture_and_review",
            status="queued",
            detail=f"取证工作流已排队，case_id={case_id}",
        )

    def submit_document_workflow(self, template_key: str, case_id: str) -> WorkflowResult:
        return WorkflowResult(
            workflow_name="document_draft",
            status="queued",
            detail=f"文书工作流已排队，template_key={template_key}, case_id={case_id}",
        )

    def schedule_monitoring(self, target: str) -> WorkflowResult:
        return WorkflowResult(
            workflow_name="monitoring",
            status="queued",
            detail=f"监控任务已排队，target={target}",
        )

