from dataclasses import dataclass
from collections.abc import Mapping, Sequence
from typing import Any

from app.services.llm import LLMGenerationResult, OpenAICompatibleLLMService


@dataclass(slots=True)
class WorkflowResult:
    workflow_name: str
    status: str
    detail: str


class HermesOrchestrator:
    def __init__(self, llm_service: OpenAICompatibleLLMService | None = None) -> None:
        self._status = "stub"
        self._llm = llm_service or OpenAICompatibleLLMService()

    def health(self) -> dict[str, str]:
        llm_health = self._llm.health()
        return {
            "name": "hermes_orchestrator",
            "status": llm_health["status"] if llm_health["status"] != "ready" else "ready",
            "description": (
                "后端工作流编排中枢，"
                f"LLM={llm_health['status']}，"
                f"{llm_health['description']}"
            ),
        }

    def submit_capture_workflow(self, case_id: str) -> WorkflowResult:
        return WorkflowResult(
            workflow_name="capture_and_review",
            status="completed",
            detail=f"取证工作流已执行，case_id={case_id}",
        )

    def submit_document_workflow(self, template_key: str, case_id: str) -> WorkflowResult:
        return WorkflowResult(
            workflow_name="document_draft",
            status="completed",
            detail=f"文书编排已执行，template_key={template_key}, case_id={case_id}",
        )

    def schedule_monitoring(self, target: str) -> WorkflowResult:
        return WorkflowResult(
            workflow_name="monitoring",
            status="scheduled",
            detail=f"监控任务已登记，target={target}",
        )

    def generate_case_summary(
        self,
        *,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]] | None = None,
        model: str | None = None,
        max_completion_tokens: int = 1024,
    ) -> LLMGenerationResult:
        return self._llm.generate_case_summary(
            case_context=case_context,
            evidence_context=evidence_context,
            model=model,
            max_completion_tokens=max_completion_tokens,
        )

    def generate_document_draft(
        self,
        *,
        template_name: str,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]] | None = None,
        variables_override: Mapping[str, str] | None = None,
        model: str | None = None,
        max_completion_tokens: int = 1536,
    ) -> LLMGenerationResult:
        return self._llm.generate_document_draft(
            template_name=template_name,
            case_context=case_context,
            evidence_context=evidence_context,
            variables_override=variables_override,
            model=model,
            max_completion_tokens=max_completion_tokens,
        )
