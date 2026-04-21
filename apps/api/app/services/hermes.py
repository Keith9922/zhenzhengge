from __future__ import annotations

from dataclasses import dataclass
import json
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from typing import Any

from app.core.config import Settings, settings as global_settings
from app.services.llm import LLMGenerationResult, OpenAICompatibleLLMService


@dataclass(slots=True)
class WorkflowResult:
    workflow_name: str
    status: str
    detail: str


class HarnessAgentRuntime:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @property
    def enabled(self) -> bool:
        return self.settings.harness_agent_enabled

    @property
    def command(self) -> str:
        return self.settings.harness_cli_command.strip() or "hermes"

    @property
    def available(self) -> bool:
        return shutil.which(self.command) is not None

    def health(self) -> dict[str, str]:
        if not self.enabled:
            return {
                "status": "disabled",
                "description": "Harness/Hermes Agent CLI 未启用",
            }
        if not self.available:
            return {
                "status": "degraded",
                "description": f"已启用 Harness/Hermes Agent，但未找到命令：{self.command}",
            }
        return {
            "status": "ready",
            "description": f"Harness/Hermes Agent CLI 可用，command={self.command}",
        }

    def run_skill_prompt(
        self,
        *,
        prompt: str,
        skills: Sequence[str],
    ) -> tuple[bool, str, str]:
        if not self.enabled:
            return False, "", "Harness/Hermes Agent CLI 未启用"
        if not self.available:
            return False, "", f"未找到 Harness/Hermes CLI 命令：{self.command}"

        cmd = [self.command, "chat", "-Q", "-q", prompt]

        provider = self.settings.harness_provider.strip()
        if provider and provider != "auto":
            cmd.extend(["--provider", provider])
        model = self.settings.harness_model.strip()
        if model:
            cmd.extend(["--model", model])

        for skill in skills:
            normalized = skill.strip()
            if normalized:
                cmd.extend(["-s", normalized])

        toolsets = [item.strip() for item in self.settings.harness_toolsets.split(",") if item.strip()]
        if toolsets:
            cmd.extend(["--toolsets", ",".join(toolsets)])

        try:
            completed = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=max(10, int(self.settings.harness_timeout_seconds)),
            )
        except Exception as exc:  # pragma: no cover
            return False, "", f"Harness/Hermes CLI 调用失败：{exc}"

        if completed.returncode != 0:
            stderr = (completed.stderr or "").strip()
            return False, "", f"Harness/Hermes CLI 返回非零退出码({completed.returncode})：{stderr}"

        content = (completed.stdout or "").strip()
        if not content:
            return False, "", "Harness/Hermes CLI 返回空内容"
        return True, content, "Harness/Hermes CLI 调用成功"


class HermesOrchestrator:
    def __init__(self, llm_service: OpenAICompatibleLLMService | None = None, settings: Settings | None = None) -> None:
        self.settings = settings or global_settings
        self._llm = llm_service or OpenAICompatibleLLMService(self.settings)
        self._harness = HarnessAgentRuntime(self.settings)

    def health(self) -> dict[str, str]:
        llm_health = self._llm.health()
        harness_health = self._harness.health()
        if harness_health["status"] == "ready":
            status = "ready"
            engine = "harness_cli"
        elif llm_health["status"] == "ready":
            status = "ready"
            engine = "llm"
        elif harness_health["status"] == "disabled":
            status = llm_health["status"]
            engine = "llm-fallback"
        else:
            status = "degraded"
            engine = "fallback"
        return {
            "name": "hermes_orchestrator",
            "status": status,
            "description": (
                f"后端工作流编排中枢，engine={engine}；"
                f"Harness={harness_health['status']}；LLM={llm_health['status']}"
            ),
        }

    def submit_capture_workflow(
        self,
        case_id: str,
        *,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]] | None = None,
    ) -> WorkflowResult:
        result = self.generate_case_summary(
            case_context=case_context,
            evidence_context=evidence_context,
        )
        if result.status == "ok" and result.content:
            return WorkflowResult(
                workflow_name="capture_and_review",
                status="completed",
                detail=result.content,
            )
        return WorkflowResult(
            workflow_name="capture_and_review",
            status="fallback",
            detail=result.detail or f"摘要生成未返回内容，case_id={case_id}",
        )

    def submit_document_workflow(
        self,
        template_key: str,
        case_id: str,
        *,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]] | None = None,
    ) -> WorkflowResult:
        if not case_context.get("title"):
            return WorkflowResult(
                workflow_name="document_draft",
                status="skipped",
                detail=f"案件信息不完整，跳过预检，case_id={case_id}",
            )
        evidence_count = len(evidence_context or [])
        if evidence_count == 0:
            return WorkflowResult(
                workflow_name="document_draft",
                status="skipped",
                detail=f"尚无证据包，跳过文书预检，case_id={case_id}",
            )
        return WorkflowResult(
            workflow_name="document_draft",
            status="ready",
            detail=f"文书预检通过，template_key={template_key}，证据包数={evidence_count}，case_id={case_id}",
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
        payload = {
            "task": "case_summary",
            "case_context": dict(case_context),
            "evidence_context": list(evidence_context or []),
            "instruction": "请生成结构化中文 Markdown 案件摘要，不要输出终局法律结论。",
        }
        harness_result = self._generate_with_harness(task_name="case_summary", payload=payload)
        if harness_result is not None:
            return harness_result
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
        payload = {
            "task": "document_draft",
            "template_name": template_name,
            "case_context": dict(case_context),
            "evidence_context": list(evidence_context or []),
            "variables_override": dict(variables_override or {}),
            "instruction": (
                "请生成可审核中文 Markdown 文书草稿；每条核心主张请标注 EvidenceID；"
                "必须体现证据来源与人工审核边界。"
            ),
        }
        harness_result = self._generate_with_harness(task_name="document_draft", payload=payload)
        if harness_result is not None:
            return harness_result
        return self._llm.generate_document_draft(
            template_name=template_name,
            case_context=case_context,
            evidence_context=evidence_context,
            variables_override=variables_override,
            model=model,
            max_completion_tokens=max_completion_tokens,
        )

    def _generate_with_harness(
        self,
        *,
        task_name: str,
        payload: Mapping[str, Any],
    ) -> LLMGenerationResult | None:
        default_skills = [item.strip() for item in self.settings.harness_skills.split(",") if item.strip()]
        # Hermes v0.10+ 内置技能名与早期版本不同，默认改为当前可用技能。
        required_skill = "wps-word" if task_name == "document_draft" else "hermes-agent"
        if required_skill not in default_skills:
            default_skills = [*default_skills, required_skill]
        prompt = self._build_harness_prompt(task_name=task_name, payload=payload)
        ok, content, detail = self._harness.run_skill_prompt(prompt=prompt, skills=default_skills)
        if not ok:
            return None
        return LLMGenerationResult(
            task_name=task_name,
            provider="harness-hermes-cli",
            model=self.settings.harness_model or "default",
            status="ok",
            content=content,
            detail=detail,
        )

    @staticmethod
    def _build_harness_prompt(*, task_name: str, payload: Mapping[str, Any]) -> str:
        serialized = json.dumps(payload, ensure_ascii=False, indent=2, default=str)
        return (
            f"你是证证鸽后端编排 Agent。请完成任务：{task_name}。\n"
            "输出要求：\n"
            "1) 仅输出最终可用 Markdown 正文。\n"
            "2) 不要输出思考过程。\n"
            "3) 对证据引用要包含 EvidenceID 字段。\n"
            f"输入：\n{serialized}\n"
        )
