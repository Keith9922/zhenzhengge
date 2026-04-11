from fastapi import APIRouter

from app.api.v1.endpoints.cases import router as cases_router
from app.api.v1.endpoints.evidence import router as evidence_router
from app.api.v1.endpoints.intake import router as intake_router
from app.api.v1.endpoints.runtime import router as runtime_router
from app.api.v1.endpoints.templates import router as templates_router

api_router = APIRouter()

api_router.include_router(intake_router, prefix="/evidence", tags=["插件 intake"])
api_router.include_router(cases_router, prefix="/cases", tags=["案件"])
api_router.include_router(evidence_router, prefix="/evidence-packs", tags=["证据包"])
api_router.include_router(templates_router, prefix="/document-templates", tags=["文书模板"])
api_router.include_router(runtime_router, prefix="/runtime", tags=["运行时"])
