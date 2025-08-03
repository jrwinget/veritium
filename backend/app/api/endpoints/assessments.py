from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.db.database import get_db
from app.services.assessment_service import AssessmentService
from pydantic import BaseModel

router = APIRouter()

class CreateAssessmentRequest(BaseModel):
    document_id: int
    user_claim: str

class AssessmentResponse(BaseModel):
    id: int
    document_id: int
    user_claim: str
    similarity_score: float
    stance: str
    entailment_score: float
    method_quality_score: float
    evidence_strength_score: float
    confidence_score: float
    explanation: str
    evidence_snippets: List[dict]
    citations: List[dict]
    share_id: Optional[str]
    created_at: str

class FeedbackRequest(BaseModel):
    feedback_score: int  # 1 for thumbs up, -1 for thumbs down
    feedback_comment: Optional[str] = None

@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    request: CreateAssessmentRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    assessment = await service.create_assessment(
        document_id=request.document_id,
        user_claim=request.user_claim
    )
    
    return AssessmentResponse(
        id=assessment.id,
        document_id=assessment.document_id,
        user_claim=assessment.user_claim,
        similarity_score=assessment.similarity_score,
        stance=assessment.stance or "neutral",
        entailment_score=assessment.entailment_score,
        method_quality_score=assessment.method_quality_score,
        evidence_strength_score=assessment.evidence_strength_score,
        confidence_score=assessment.confidence_score,
        explanation=assessment.explanation or "",
        evidence_snippets=assessment.evidence_snippets or [],
        citations=assessment.citations or [],
        share_id=assessment.share_id,
        created_at=assessment.created_at.isoformat()
    )

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: int, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    assessment = await service.get_assessment(assessment_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return AssessmentResponse(
        id=assessment.id,
        document_id=assessment.document_id,
        user_claim=assessment.user_claim,
        similarity_score=assessment.similarity_score,
        stance=assessment.stance or "neutral",
        entailment_score=assessment.entailment_score,
        method_quality_score=assessment.method_quality_score,
        evidence_strength_score=assessment.evidence_strength_score,
        confidence_score=assessment.confidence_score,
        explanation=assessment.explanation or "",
        evidence_snippets=assessment.evidence_snippets or [],
        citations=assessment.citations or [],
        share_id=assessment.share_id,
        created_at=assessment.created_at.isoformat()
    )

@router.get("/share/{share_id}", response_model=AssessmentResponse)
async def get_shared_assessment(share_id: str, db: AsyncSession = Depends(get_db)):
    service = AssessmentService(db)
    assessment = await service.get_assessment_by_share_id(share_id)
    
    if not assessment:
        raise HTTPException(status_code=404, detail="Shared assessment not found")
    
    return AssessmentResponse(
        id=assessment.id,
        document_id=assessment.document_id,
        user_claim=assessment.user_claim,
        similarity_score=assessment.similarity_score,
        stance=assessment.stance or "neutral",
        entailment_score=assessment.entailment_score,
        method_quality_score=assessment.method_quality_score,
        evidence_strength_score=assessment.evidence_strength_score,
        confidence_score=assessment.confidence_score,
        explanation=assessment.explanation or "",
        evidence_snippets=assessment.evidence_snippets or [],
        citations=assessment.citations or [],
        share_id=assessment.share_id,
        created_at=assessment.created_at.isoformat()
    )

@router.post("/{assessment_id}/feedback")
async def submit_feedback(
    assessment_id: int,
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    service = AssessmentService(db)
    success = await service.submit_feedback(
        assessment_id=assessment_id,
        feedback_score=request.feedback_score,
        feedback_comment=request.feedback_comment
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    return {"message": "Feedback submitted successfully"}