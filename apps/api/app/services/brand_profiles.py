from __future__ import annotations

import json

from app.core.storage import SQLiteStorage
from app.schemas.brand_profiles import (
    BrandProfileCreateRequest,
    BrandProfileRecord,
    BrandProfileUpdateRequest,
)
from app.services.llm import OpenAICompatibleLLMService


class BrandProfileService:
    def __init__(self, storage: SQLiteStorage, llm_service: OpenAICompatibleLLMService) -> None:
        self.storage = storage
        self.llm = llm_service

    def list_profiles(self, *, organization_id: str | None = None) -> list[BrandProfileRecord]:
        return self.storage.list_brand_profiles(organization_id=organization_id)

    def get_profile(self, profile_id: str, *, organization_id: str | None = None) -> BrandProfileRecord | None:
        return self.storage.get_brand_profile(profile_id, organization_id=organization_id)

    def create_profile(
        self,
        payload: BrandProfileCreateRequest,
        *,
        organization_id: str,
        owner_user_id: str,
    ) -> BrandProfileRecord:
        return self.storage.create_brand_profile(payload, organization_id=organization_id, owner_user_id=owner_user_id)

    def update_profile(
        self,
        profile_id: str,
        payload: BrandProfileUpdateRequest,
        *,
        organization_id: str | None = None,
    ) -> BrandProfileRecord | None:
        return self.storage.update_brand_profile(profile_id, payload, organization_id=organization_id)

    def delete_profile(self, profile_id: str, *, organization_id: str | None = None) -> bool:
        return self.storage.delete_brand_profile(profile_id, organization_id=organization_id)

    def suggest_confusable(self, brand_name: str) -> list[str]:
        system_prompt = (
            "你是知识产权领域的专家助手。"
            "请根据给定的品牌名称，列举可能造成消费者混淆的形近字、谐音字、同音字变体，"
            "以及常见的仿冒命名手法（如替换单个字、添加前缀/后缀、使用同音字等）。"
            "直接输出一个 JSON 数组，每项为一个字符串，不要输出任何其他内容。"
            "示例输出格式：[\"变体1\", \"变体2\", \"变体3\"]"
            "至少给出 8 个，最多 15 个。只输出 JSON 数组，不含 markdown 代码块。"
        )
        result = self.llm._generate_chat_completion(
            task_name="suggest_confusable",
            system_prompt=system_prompt,
            user_prompt=f"品牌名称：{brand_name}",
            model=self.llm.default_text_model,
            max_completion_tokens=512,
            temperature=0.3,
            top_p=None,
            fallback_content="[]",
            fallback_detail="LLM 不可用，返回空列表",
        )
        content = result.content.strip()
        # strip markdown code fences if present
        if content.startswith("```"):
            content = "\n".join(
                line for line in content.splitlines()
                if not line.startswith("```")
            ).strip()
        try:
            suggestions = json.loads(content)
            if isinstance(suggestions, list):
                return [str(s) for s in suggestions if s]
        except (json.JSONDecodeError, ValueError):
            pass
        return []

    def get_risk_keywords_for_org(self, organization_id: str) -> list[str]:
        """返回该组织所有品牌档案的 protection_keywords + confusable_terms 合集，用于风险评分。"""
        profiles = self.list_profiles(organization_id=organization_id)
        keywords: list[str] = []
        for p in profiles:
            keywords.extend(p.protection_keywords)
            keywords.extend(p.confusable_terms)
            keywords.append(p.brand_name)
        # 去重、保序
        seen: set[str] = set()
        result: list[str] = []
        for kw in keywords:
            kw = kw.strip()
            if kw and kw not in seen:
                seen.add(kw)
                result.append(kw)
        return result

    def match_brand_for_text(self, text: str, organization_id: str) -> str | None:
        """从 org 的品牌档案中找到与页面文本最相关的品牌名，用于替换 intake 里猜出来的 brand_name。"""
        profiles = self.list_profiles(organization_id=organization_id)
        if not profiles:
            return None
        text_lower = text.lower()
        best: tuple[int, str] | None = None
        for p in profiles:
            all_terms = [p.brand_name] + p.protection_keywords + p.confusable_terms
            hits = sum(1 for term in all_terms if term.strip().lower() in text_lower)
            if hits > 0:
                if best is None or hits > best[0]:
                    best = (hits, p.brand_name)
        return best[1] if best else None
