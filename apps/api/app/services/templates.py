from app.schemas.templates import DocumentTemplateSummary


class DocumentTemplateService:
    def __init__(self) -> None:
        self._templates = [
            DocumentTemplateSummary(
                template_key="lawyer-letter",
                name="律师函",
                category="处置文书",
                description="用于向平台或相对方发出的侵权处置初稿。",
                target_use="法务审核前草稿",
                output_formats=["docx", "pdf"],
            ),
            DocumentTemplateSummary(
                template_key="platform-complaint",
                name="平台投诉函",
                category="处置文书",
                description="用于向电商平台提交投诉材料的初稿。",
                target_use="平台治理与下架申请",
                output_formats=["docx", "pdf"],
            ),
            DocumentTemplateSummary(
                template_key="evidence-index",
                name="证据目录",
                category="案件材料",
                description="用于整理证据包与案件说明的材料模板。",
                target_use="案件归档与审核",
                output_formats=["docx"],
            ),
        ]

    def list_templates(self) -> list[DocumentTemplateSummary]:
        return list(self._templates)

