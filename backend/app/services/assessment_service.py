import uuid
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.document import Document, Assessment
from app.services.similarity_service import SimilarityService
from app.services.explanation_service import ExplanationService


class AssessmentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.similarity_service = SimilarityService()
        self.explanation_service = ExplanationService()

    async def create_assessment(self, document_id: int, user_claim: str) -> Assessment:
        # Get the document
        result = await self.db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError("Document not found")

        # Calculate similarity with document claims
        similarity_result = await self.similarity_service.calculate_similarity(
            user_claim=user_claim,
            document_claims=document.extracted_claims or [],
            document_content=document.content or "",
        )

        # Calculate entailment/stance
        entailment_result = await self.similarity_service.calculate_entailment_score(
            user_claim=user_claim, evidence_text=document.content or ""
        )

        # Calculate component scores
        method_quality_score = document.method_quality_score
        evidence_strength_score = self._calculate_evidence_strength(
            similarity_result, entailment_result
        )

        # Calculate overall confidence
        confidence_score = self._calculate_confidence_score(
            similarity_result["similarity_score"],
            entailment_result["entailment_score"],
            method_quality_score,
            evidence_strength_score,
        )

        # Generate explanation
        explanation = await self.explanation_service.generate_explanation(
            user_claim=user_claim,
            document=document,
            similarity_result=similarity_result,
            entailment_result=entailment_result,
            confidence_score=confidence_score,
        )

        # Create citations
        citations = self._create_citations(
            similarity_result["evidence_snippets"], document
        )

        # Generate share ID
        share_id = str(uuid.uuid4())

        # Create assessment record
        assessment = Assessment(
            document_id=document_id,
            user_claim=user_claim,
            similarity_score=similarity_result["similarity_score"],
            stance=entailment_result["stance"],
            entailment_score=entailment_result["entailment_score"],
            method_quality_score=method_quality_score,
            evidence_strength_score=evidence_strength_score,
            confidence_score=confidence_score,
            explanation=explanation,
            evidence_snippets=similarity_result["evidence_snippets"],
            citations=citations,
            share_id=share_id,
        )

        self.db.add(assessment)
        await self.db.commit()
        await self.db.refresh(assessment)

        return assessment

    async def get_assessment(self, assessment_id: int) -> Optional[Assessment]:
        result = await self.db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        return result.scalar_one_or_none()

    async def get_assessment_by_share_id(self, share_id: str) -> Optional[Assessment]:
        result = await self.db.execute(
            select(Assessment).where(Assessment.share_id == share_id)
        )
        return result.scalar_one_or_none()

    async def submit_feedback(
        self,
        assessment_id: int,
        feedback_score: int,
        feedback_comment: Optional[str] = None,
    ) -> bool:
        result = await self.db.execute(
            select(Assessment).where(Assessment.id == assessment_id)
        )
        assessment = result.scalar_one_or_none()

        if not assessment:
            return False

        assessment.feedback_score = feedback_score
        assessment.feedback_comment = feedback_comment

        await self.db.commit()
        return True

    def _calculate_evidence_strength(
        self, similarity_result: Dict[str, Any], entailment_result: Dict[str, Any]
    ) -> float:
        # Combine similarity and entailment to determine evidence strength
        similarity_score = similarity_result["similarity_score"]
        entailment_score = entailment_result["entailment_score"]

        # Number of evidence snippets found
        num_evidence = len(similarity_result["evidence_snippets"])
        evidence_bonus = min(
            0.2, num_evidence * 0.05
        )  # Up to 0.2 bonus for multiple evidence

        # Weighted combination
        strength_score = (
            0.4 * similarity_score + 0.4 * entailment_score + 0.2 * evidence_bonus
        )

        return min(max(strength_score, 0.0), 1.0)

    def _calculate_confidence_score(
        self,
        similarity_score: float,
        entailment_score: float,
        method_quality_score: float,
        evidence_strength_score: float,
    ) -> float:
        # Weighted combination of all component scores
        weights = {
            "similarity": 0.25,
            "entailment": 0.25,
            "method_quality": 0.30,
            "evidence_strength": 0.20,
        }

        confidence = (
            weights["similarity"] * similarity_score
            + weights["entailment"] * entailment_score
            + weights["method_quality"] * method_quality_score
            + weights["evidence_strength"] * evidence_strength_score
        )

        # Add uncertainty band - reduce confidence if scores are inconsistent
        score_variance = self._calculate_score_variance(
            [
                similarity_score,
                entailment_score,
                method_quality_score,
                evidence_strength_score,
            ]
        )

        # Higher variance reduces confidence
        uncertainty_penalty = min(0.2, score_variance * 0.5)
        confidence = confidence - uncertainty_penalty

        return min(max(confidence, 0.0), 1.0)

    def _calculate_score_variance(self, scores: list) -> float:
        if len(scores) < 2:
            return 0.0

        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)

        return variance

    def _create_citations(self, evidence_snippets: list, document: Document) -> list:
        citations = []

        for i, snippet in enumerate(evidence_snippets):
            citation = {
                "id": f"citation_{i + 1}",
                "text": snippet["text"],
                "similarity_score": snippet["similarity"],
                "document_title": document.title,
                "document_id": document.id,
                "snippet_index": snippet.get("sentence_index", i),
            }

            # Add DOI or URL if available
            if document.doi:
                citation["doi"] = document.doi
            elif document.url:
                citation["url"] = document.url

            citations.append(citation)

        return citations
