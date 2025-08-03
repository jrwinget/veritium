from fastapi import APIRouter
from app.api.endpoints import documents, assessments

router = APIRouter()

router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])