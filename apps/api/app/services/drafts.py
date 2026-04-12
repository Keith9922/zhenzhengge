from pathlib import Path
import re

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from app.core.storage import SQLiteStorage
from app.schemas.drafts import DocumentDraftCreateRequest, DocumentDraftRecord, DraftStatus
from app.services.cases import CaseService
from app.services.evidence import EvidenceService
from app.services.hermes import HermesOrchestrator
from app.services.templates import DocumentTemplateService


class DocumentDraftService:
    def __init__(
        self,
        storage: SQLiteStorage,
        *,
        case_service: CaseService,
        template_service: DocumentTemplateService,
        evidence_service: EvidenceService,
        hermes: HermesOrchestrator,
    ) -> None:
        self.storage = storage
        self.case_service = case_service
        self.template_service = template_service
        self.evidence_service = evidence_service
        self.hermes = hermes

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
        _ = self.hermes.submit_document_workflow(template.template_key, case.case_id)
        evidence_items = self.evidence_service.list_packs(case.case_id)
        llm_result = self.hermes.generate_document_draft(
            template_name=template.name,
            case_context={
                "case_id": case.case_id,
                "title": case.title,
                "brand_name": case.brand_name,
                "suspect_name": case.suspect_name,
                "platform": case.platform,
                "risk_level": case.risk_level,
                "description": case.description,
            },
            evidence_context=[self._build_evidence_context(item) for item in evidence_items],
            variables_override=payload.variables_override,
        )
        content = llm_result.content or self._render_content(
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
        export_path = export_dir / f"{draft_id}.docx"

        doc = Document()
        self._configure_document(doc)

        title = doc.add_heading(draft.title or "文书草稿", 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta = doc.add_paragraph()
        meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        meta.add_run(f"案件编号：{draft.case_id}  ").bold = True
        meta.add_run(f"模板：{draft.template_key}  ")
        meta.add_run(f"导出时间：{draft.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")

        lines = (draft.content or "").strip().split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line == "---":
                doc.add_paragraph()
                continue
            # Handle headings
            if line.startswith("# "):
                doc.add_heading(line[2:], level=1)
            elif line.startswith("## "):
                doc.add_heading(line[3:], level=2)
            elif line.startswith("### "):
                doc.add_heading(line[4:], level=3)
            elif re.match(r"^\d+\.\s+", line):
                p = doc.add_paragraph(style="List Number")
                self._append_inline_runs(p, re.sub(r"^\d+\.\s+", "", line))
            # Handle list items
            elif line.startswith("- "):
                p = doc.add_paragraph(style="List Bullet")
                self._append_inline_runs(p, line[2:])
            elif line.startswith("> "):
                p = doc.add_paragraph()
                p.paragraph_format.left_indent = Inches(0.28)
                run = p.add_run(line[2:])
                run.italic = True
            else:
                p = doc.add_paragraph()
                self._append_inline_runs(p, line)

        doc.save(str(export_path))

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

    def _build_evidence_context(self, item) -> dict[str, str]:
        return {
            "evidence_pack_id": item.evidence_pack_id,
            "source_title": item.source_title,
            "source_url": item.source_url,
            "note": item.note or "",
            "capture_channel": item.capture_channel,
            "captured_at": item.created_at.isoformat(),
            "hash_sha256": item.hash_sha256,
            "html_excerpt": self._extract_html_excerpt(self.evidence_service.read_html(item)),
        }

    @staticmethod
    def _extract_html_excerpt(raw_html: str, limit: int = 160) -> str:
        text = re.sub(r"<script[\s\S]*?</script>", " ", raw_html, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        if len(text) <= limit:
            return text
        return f"{text[:limit].rstrip()}..."

    @staticmethod
    def _append_inline_runs(paragraph, text: str) -> None:
        parts = re.split(r"\*\*(.+?)\*\*", text)
        for index, part in enumerate(parts):
            run = paragraph.add_run(part)
            if index % 2 == 1:
                run.bold = True

    @staticmethod
    def _configure_document(doc: Document) -> None:
        section = doc.sections[0]
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

        normal_style = doc.styles["Normal"]
        DocumentDraftService._set_style_font(normal_style, "宋体", 11)

        heading1 = doc.styles["Heading 1"]
        DocumentDraftService._set_style_font(heading1, "黑体", 14)

        heading2 = doc.styles["Heading 2"]
        DocumentDraftService._set_style_font(heading2, "黑体", 12)

    @staticmethod
    def _set_style_font(style, font_name: str, size: int) -> None:
        style.font.name = font_name
        style.font.size = Pt(size)
        style._element.get_or_add_rPr().get_or_add_rFonts().set(qn("w:eastAsia"), font_name)
