from fastapi import APIRouter, Depends

from app.api.deps import get_template_service
from app.api.security import CurrentUser, require_roles
from app.schemas.templates import DocumentTemplateListResponse
from app.services.templates import DocumentTemplateService

router = APIRouter()


@router.get("", response_model=DocumentTemplateListResponse, summary="文书模板列表")
def list_document_templates(
    service: DocumentTemplateService = Depends(get_template_service),
    _: CurrentUser = Depends(require_roles("viewer", "operator", "admin")),
) -> DocumentTemplateListResponse:
    items = service.list_templates()
    return DocumentTemplateListResponse(total=len(items), items=items)
