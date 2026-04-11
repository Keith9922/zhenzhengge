from pydantic import BaseModel


class DocumentTemplateSummary(BaseModel):
    template_key: str
    name: str
    category: str
    description: str
    target_use: str
    output_formats: list[str]
    is_active: bool = True


class DocumentTemplateListResponse(BaseModel):
    total: int
    items: list[DocumentTemplateSummary]

