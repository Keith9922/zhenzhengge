from pathlib import Path

from app.core.storage import SQLiteStorage
from app.schemas.drafts import DocumentDraftCreateRequest, DocumentDraftRecord, DraftStatus
from app.services.cases import CaseService
from app.services.templates import DocumentTemplateService


class DocumentDraftService:
    def __init__(
        self,
        storage: SQLiteStorage,
        *,
        case_service: CaseService,
        template_service: DocumentTemplateService,
    ) -> None:
        self.storage = storage
        self.case_service = case_service
        self.template_service = template_service

    def list_drafts(self, case_id: str | None = None) -> list[DocumentDraftRecord]:
        return self.storage.list_document_drafts(case_id=case_id)

    def get_draft(self, draft_id: str) -> DocumentDraftRecord | None:
        return self.storage.get_document_draft(draft_id)

    def generate_draft(self, payload: DocumentDraftCreateRequest) -> DocumentDraftRecord:
        case = self.case_service.get_case(payload.case_id)
        if case is None:
            raise ValueError("案件不存在")

        template = self.template_service.get_template(payload.template_key)
        if template is None:
            raise ValueError("模板不存在")

        title = f"{case.title} - {template.name}"
        content = self._render_content(
            case_title=case.title,
            brand_name=case.brand_name,
            suspect_name=case.suspect_name,
            platform=case.platform,
            risk_level=case.risk_level,
            description=case.description,
            template_name=template.name,
            extra_variables=payload.variables_override,
        )
        return self.storage.create_document_draft(
            case_id=payload.case_id,
            template_key=payload.template_key,
            title=title,
            content=content,
        )

    def submit_review(self, draft_id: str, comment: str) -> DocumentDraftRecord | None:
        return self.storage.update_document_draft_review(
            draft_id=draft_id,
            status=DraftStatus.submitted,
            review_comment=comment,
        )

    def approve(self, draft_id: str, comment: str) -> DocumentDraftRecord | None:
        return self.storage.update_document_draft_review(
            draft_id=draft_id,
            status=DraftStatus.approved,
            review_comment=comment,
        )

    def reject(self, draft_id: str, comment: str) -> DocumentDraftRecord | None:
        return self.storage.update_document_draft_review(
            draft_id=draft_id,
            status=DraftStatus.rejected,
            review_comment=comment,
        )

    def export_draft(self, draft_id: str) -> DocumentDraftRecord | None:
        draft = self.storage.get_document_draft(draft_id)
        if draft is None:
            return None

        base_dir = Path(self.storage.db_path).resolve().parent if self.storage.db_path != ":memory:" else Path.cwd()
        export_dir = base_dir / "exports" / "drafts"
        export_dir.mkdir(parents=True, exist_ok=True)
        export_path = export_dir / f"{draft_id}.md"
        export_path.write_text(draft.content, encoding="utf-8")

        relative_path = export_path.relative_to(base_dir).as_posix()
        return self.storage.set_document_draft_export_path(draft_id, relative_path)

    def _render_content(
        self,
        *,
        case_title: str,
        brand_name: str,
        suspect_name: str,
        platform: str,
        risk_level: str,
        description: str,
        template_name: str,
        extra_variables: dict[str, str],
    ) -> str:
        extra_text = "\n".join(f"- {key}: {value}" for key, value in extra_variables.items()) or "- 无"
        return (
            f"# {template_name}\n\n"
            f"## 案件标题\n{case_title}\n\n"
            f"## 品牌对象\n{brand_name}\n\n"
            f"## 疑似主体\n{suspect_name}\n\n"
            f"## 来源平台\n{platform}\n\n"
            f"## 风险等级\n{risk_level}\n\n"
            f"## 案件说明\n{description}\n\n"
            f"## 补充变量\n{extra_text}\n\n"
            "## 使用提示\n"
            "本草稿用于内部整理和法务审核前预览，正式对外动作仍需人工确认。\n"
        )
