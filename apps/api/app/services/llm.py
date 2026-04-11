from __future__ import annotations

from dataclasses import dataclass
import json
from collections.abc import Mapping, Sequence
from typing import Any

from app.core.config import Settings, settings as global_settings

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - dependency is optional during import-time checks
    OpenAI = None  # type: ignore[assignment]


_DISABLED_PROVIDERS = {"", "stub", "placeholder", "disabled", "off"}


@dataclass(slots=True)
class LLMGenerationResult:
    task_name: str
    provider: str
    model: str
    status: str
    content: str
    detail: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class OpenAICompatibleLLMService:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or global_settings
        self._client: Any | None = None

    @property
    def provider(self) -> str:
        return self.settings.llm_provider.strip().lower()

    @property
    def is_enabled(self) -> bool:
        return (
            self.provider not in _DISABLED_PROVIDERS
            and bool(self.settings.llm_api_key.strip())
            and bool(self.settings.llm_base_url.strip())
        )

    @property
    def default_text_model(self) -> str:
        return self.settings.llm_model.strip() or "mimo-v2-pro"

    @property
    def default_reasoning_model(self) -> str:
        return self.settings.llm_reasoning_model.strip() or self.default_text_model

    def health(self) -> dict[str, str]:
        if not self.is_enabled:
            return {
                "name": "llm_client",
                "status": "stub",
                "description": "LLM 客户端未启用，当前使用本地回退文本",
            }
        if OpenAI is None:
            return {
                "name": "llm_client",
                "status": "degraded",
                "description": f"provider={self.provider}，但 openai SDK 未安装",
            }
        return {
            "name": "llm_client",
            "status": "ready",
            "description": (
                f"provider={self.provider}, "
                f"base_url={self.settings.llm_base_url.strip()}, "
                f"model={self.default_text_model}"
            ),
        }

    def generate_case_summary(
        self,
        *,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]] | None = None,
        model: str | None = None,
        max_completion_tokens: int = 1024,
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> LLMGenerationResult:
        system_prompt = (
            "你是证证鸽的案件摘要助手。"
            "请根据结构化案件信息和证据要点，输出适合工作台展示的中文 Markdown 摘要。"
            "不要编造证据，不要输出法律终局结论。"
        )
        user_prompt = self._format_json_payload(
            {
                "case_context": case_context,
                "evidence_context": list(evidence_context or []),
            }
        )
        return self._generate_chat_completion(
            task_name="case_summary",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model or self.default_reasoning_model,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            top_p=top_p,
            fallback_content=self._build_case_summary_fallback(case_context, evidence_context or []),
            fallback_detail="案件摘要使用本地回退逻辑生成",
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
        temperature: float | None = None,
        top_p: float | None = None,
    ) -> LLMGenerationResult:
        system_prompt = (
            "你是证证鸽的知识产权文书初稿助手。"
            "请根据模板名、案件信息、证据要点和补充变量，输出可供法务审核的中文 Markdown 草稿。"
            "不要把未确认事实写成既成结论，不要直接输出最终定稿版本。"
        )
        user_prompt = self._format_json_payload(
            {
                "template_name": template_name,
                "case_context": case_context,
                "evidence_context": list(evidence_context or []),
                "variables_override": dict(variables_override or {}),
            }
        )
        return self._generate_chat_completion(
            task_name="document_draft",
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model or self.default_text_model,
            max_completion_tokens=max_completion_tokens,
            temperature=temperature,
            top_p=top_p,
            fallback_content=self._build_document_draft_fallback(
                template_name=template_name,
                case_context=case_context,
                evidence_context=evidence_context or [],
                variables_override=variables_override or {},
            ),
            fallback_detail="文书草稿使用本地回退逻辑生成",
        )

    def _generate_chat_completion(
        self,
        *,
        task_name: str,
        system_prompt: str,
        user_prompt: str,
        model: str,
        max_completion_tokens: int,
        temperature: float | None,
        top_p: float | None,
        fallback_content: str,
        fallback_detail: str,
    ) -> LLMGenerationResult:
        if not self.is_enabled:
            return LLMGenerationResult(
                task_name=task_name,
                provider=self.provider or "stub",
                model=model,
                status="stub",
                content=fallback_content,
                detail=fallback_detail,
            )

        client = self._get_client()
        if client is None:
            return LLMGenerationResult(
                task_name=task_name,
                provider=self.provider or "stub",
                model=model,
                status="degraded",
                content=fallback_content,
                detail="openai SDK 不可用，已回退到本地模板",
            )

        try:
            kwargs: dict[str, Any] = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_completion_tokens": max_completion_tokens,
            }
            if temperature is not None:
                kwargs["temperature"] = temperature
            if top_p is not None:
                kwargs["top_p"] = top_p

            response = client.chat.completions.create(**kwargs)
            content = self._extract_message_content(response)
            if not content.strip():
                retry_response = client.chat.completions.create(
                    **{
                        **kwargs,
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    f"{system_prompt}\n"
                                    "只输出最终正文，不要输出思考过程、分析过程或任何额外说明。"
                                ),
                            },
                            {"role": "user", "content": user_prompt},
                        ],
                    }
                )
                retry_content = self._extract_message_content(retry_response)
                if retry_content.strip():
                    response = retry_response
                    content = retry_content

            if not content.strip():
                return LLMGenerationResult(
                    task_name=task_name,
                    provider=self.provider,
                    model=model,
                    status="fallback",
                    content=fallback_content,
                    detail=f"{fallback_detail}；远程调用成功但未返回可展示正文",
                )

            usage = getattr(response, "usage", None)
            return LLMGenerationResult(
                task_name=task_name,
                provider=self.provider,
                model=model,
                status="ok",
                content=content,
                detail=f"LLM 调用成功，model={model}",
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )
        except Exception as exc:  # pragma: no cover - remote call failure path
            return LLMGenerationResult(
                task_name=task_name,
                provider=self.provider,
                model=model,
                status="fallback",
                content=fallback_content,
                detail=f"{fallback_detail}；远程调用失败：{exc}",
            )

    def _get_client(self) -> Any | None:
        if self._client is not None:
            return self._client
        if OpenAI is None:
            return None
        self._client = OpenAI(
            api_key=self.settings.llm_api_key.strip(),
            base_url=self.settings.llm_base_url.strip(),
        )
        return self._client

    @staticmethod
    def _extract_message_content(response: Any) -> str:
        choices = getattr(response, "choices", None) or []
        if not choices:
            return ""
        first_choice = choices[0]
        message = getattr(first_choice, "message", None)
        if message is None:
            return ""
        content = getattr(message, "content", None)
        return content if isinstance(content, str) else ""

    @staticmethod
    def _format_json_payload(payload: Mapping[str, Any]) -> str:
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)

    def _build_case_summary_fallback(
        self,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]],
    ) -> str:
        case_title = str(case_context.get("title") or "未命名案件")
        brand_name = str(case_context.get("brand_name") or "未命名品牌")
        suspect_name = str(case_context.get("suspect_name") or "未知疑似主体")
        platform = str(case_context.get("platform") or "未知平台")
        risk_level = str(case_context.get("risk_level") or "unknown")
        description = str(case_context.get("description") or "暂无案件说明。")
        evidence_lines = self._format_evidence_lines(evidence_context)
        return (
            f"# 案件摘要\n\n"
            f"## 案件标题\n{case_title}\n\n"
            f"## 品牌对象\n{brand_name}\n\n"
            f"## 疑似主体\n{suspect_name}\n\n"
            f"## 来源平台\n{platform}\n\n"
            f"## 风险等级\n{risk_level}\n\n"
            f"## 案件说明\n{description}\n\n"
            f"## 证据要点\n{evidence_lines}\n\n"
            "## 建议动作\n"
            "- 先核对页面快照与原始链接。\n"
            "- 先固化证据包，再推进文书审核。\n"
            "- 如有争议内容，交由人工复核后再对外动作。\n"
        )

    def _build_document_draft_fallback(
        self,
        *,
        template_name: str,
        case_context: Mapping[str, Any],
        evidence_context: Sequence[Mapping[str, Any]],
        variables_override: Mapping[str, str],
    ) -> str:
        case_title = str(case_context.get("title") or "未命名案件")
        brand_name = str(case_context.get("brand_name") or "未命名品牌")
        suspect_name = str(case_context.get("suspect_name") or "未知疑似主体")
        platform = str(case_context.get("platform") or "未知平台")
        risk_level = str(case_context.get("risk_level") or "unknown")
        description = str(case_context.get("description") or "暂无案件说明。")
        variable_lines = self._format_mapping_lines(variables_override)
        evidence_lines = self._format_evidence_lines(evidence_context)
        return (
            f"# {template_name}\n\n"
            f"## 案件标题\n{case_title}\n\n"
            f"## 品牌对象\n{brand_name}\n\n"
            f"## 疑似主体\n{suspect_name}\n\n"
            f"## 来源平台\n{platform}\n\n"
            f"## 风险等级\n{risk_level}\n\n"
            f"## 案件说明\n{description}\n\n"
            f"## 证据要点\n{evidence_lines}\n\n"
            f"## 补充变量\n{variable_lines}\n\n"
            "## 初稿正文\n"
            "本草稿用于法务审核前预览，正式对外动作仍需人工确认。\n"
        )

    @staticmethod
    def _format_mapping_lines(mapping: Mapping[str, str]) -> str:
        if not mapping:
            return "- 无"
        return "\n".join(f"- {key}: {value}" for key, value in mapping.items())

    def _format_evidence_lines(self, evidence_context: Sequence[Mapping[str, Any]]) -> str:
        if not evidence_context:
            return "- 无"
        lines: list[str] = []
        for index, item in enumerate(evidence_context, start=1):
            title = str(item.get("source_title") or item.get("title") or f"证据 {index}")
            url = str(item.get("source_url") or item.get("url") or "")
            note = str(item.get("note") or item.get("summary") or "")
            parts = [f"{index}. {title}"]
            if url:
                parts.append(f"URL={url}")
            if note:
                parts.append(f"说明={note}")
            lines.append(" | ".join(parts))
        return "\n".join(f"- {line}" for line in lines)
