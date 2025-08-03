from typing import Dict, Any
from app.models.document import Document


class ExplanationService:
    def __init__(self):
        self.explanation_templates = {
            "high_confidence": {
                "supports": "The evidence strongly supports your claim. The document contains multiple relevant findings that align with your statement.",
                "contradicts": "The evidence strongly contradicts your claim. The document presents findings that directly oppose your statement.",
                "neutral": "The evidence is mixed regarding your claim. While some findings are relevant, they neither strongly support nor contradict your statement.",
            },
            "medium_confidence": {
                "supports": "The evidence moderately supports your claim. There are relevant findings, but the support is not definitive.",
                "contradicts": "The evidence suggests your claim may not be accurate. Some findings appear to contradict your statement.",
                "neutral": "The evidence provides limited insight into your claim. The document discusses related topics but doesn't directly address your specific statement.",
            },
            "low_confidence": {
                "supports": "There is weak evidence supporting your claim. The document mentions related concepts but doesn't provide strong validation.",
                "contradicts": "There is weak evidence against your claim. The document suggests some contradiction but it's not definitive.",
                "neutral": "The evidence is insufficient to evaluate your claim. The document doesn't contain enough relevant information.",
            },
        }

    async def generate_explanation(
        self,
        user_claim: str,
        document: Document,
        similarity_result: Dict[str, Any],
        entailment_result: Dict[str, Any],
        confidence_score: float,
    ) -> str:
        # Determine confidence level
        if confidence_score >= 0.7:
            confidence_level = "high_confidence"
        elif confidence_score >= 0.4:
            confidence_level = "medium_confidence"
        else:
            confidence_level = "low_confidence"

        # Get stance
        stance = entailment_result["stance"]

        # Get base explanation
        base_explanation = self.explanation_templates[confidence_level][stance]

        # Build detailed explanation
        explanation_parts = [base_explanation]

        # Add methodology assessment
        method_explanation = self._explain_methodology(document.method_quality_score)
        if method_explanation:
            explanation_parts.append(method_explanation)

        # Add similarity insights
        similarity_explanation = self._explain_similarity(similarity_result)
        if similarity_explanation:
            explanation_parts.append(similarity_explanation)

        # Add evidence strength insights
        evidence_explanation = self._explain_evidence(
            similarity_result["evidence_snippets"]
        )
        if evidence_explanation:
            explanation_parts.append(evidence_explanation)

        # Add limitations and caveats
        limitations = self._explain_limitations(confidence_score, document)
        if limitations:
            explanation_parts.append(limitations)

        return " ".join(explanation_parts)

    def _explain_methodology(self, method_quality_score: float) -> str:
        if method_quality_score >= 0.8:
            return "The study demonstrates high methodological quality with robust research design."
        elif method_quality_score >= 0.6:
            return "The study shows good methodological quality, though some limitations may exist."
        elif method_quality_score >= 0.4:
            return "The study has moderate methodological quality with noticeable limitations."
        else:
            return "The study has low methodological quality, which affects the reliability of conclusions."

    def _explain_similarity(self, similarity_result: Dict[str, Any]) -> str:
        similarity_score = similarity_result["similarity_score"]

        if similarity_score >= 0.8:
            return "Your claim closely matches the study's findings."
        elif similarity_score >= 0.6:
            return "Your claim is reasonably similar to the study's findings."
        elif similarity_score >= 0.4:
            return "Your claim has some similarity to the study's findings."
        else:
            return "Your claim has limited similarity to the study's findings."

    def _explain_evidence(self, evidence_snippets: list) -> str:
        num_snippets = len(evidence_snippets)

        if num_snippets >= 5:
            return "Multiple relevant passages were found in the document."
        elif num_snippets >= 3:
            return "Several relevant passages support this assessment."
        elif num_snippets >= 1:
            return "Some relevant passages were identified."
        else:
            return "Limited relevant evidence was found in the document."

    def _explain_limitations(self, confidence_score: float, document: Document) -> str:
        limitations = []

        if confidence_score < 0.5:
            limitations.append(
                "The assessment has low confidence due to limited evidence."
            )

        if not document.extracted_claims:
            limitations.append("No clear claims were extracted from the document.")

        if document.method_quality_score < 0.4:
            limitations.append(
                "The study's methodological limitations affect result reliability."
            )

        if not document.doi and not document.url:
            limitations.append("The document source could not be verified.")

        if limitations:
            return "Limitations: " + " ".join(limitations)

        return ""

    async def generate_detailed_explanation(
        self,
        user_claim: str,
        document: Document,
        similarity_result: Dict[str, Any],
        entailment_result: Dict[str, Any],
        confidence_score: float,
        quality_assessment: Dict[str, Any],
    ) -> Dict[str, str]:
        # Generate explanation sections

        # Executive summary
        summary = await self.generate_explanation(
            user_claim, document, similarity_result, entailment_result, confidence_score
        )

        # Methodology strengths and weaknesses
        methodology_section = self._generate_methodology_section(quality_assessment)

        # Evidence analysis
        evidence_section = self._generate_evidence_section(
            similarity_result, entailment_result
        )

        # Potential overclaiming assessment
        overclaiming_section = self._assess_overclaiming(
            user_claim, similarity_result, confidence_score
        )

        return {
            "summary": summary,
            "methodology": methodology_section,
            "evidence_analysis": evidence_section,
            "overclaiming_assessment": overclaiming_section,
        }

    def _generate_methodology_section(self, quality_assessment: Dict[str, Any]) -> str:
        sections = []

        # Sample size
        sample_details = quality_assessment.get("sample_size", {})
        if sample_details.get("max_sample_size"):
            size = sample_details["max_sample_size"]
            if size >= 1000:
                sections.append(
                    f"Large sample size (n={size}) enhances result reliability."
                )
            elif size >= 100:
                sections.append(f"Adequate sample size (n={size}) supports findings.")
            else:
                sections.append(
                    f"Small sample size (n={size}) limits generalizability."
                )

        # Statistical rigor
        stats_details = quality_assessment.get("statistical_rigor", {})
        if stats_details.get("p_values_found"):
            sections.append("Statistical significance testing was employed.")

        # Peer review
        peer_review_details = quality_assessment.get("peer_review", {})
        if peer_review_details.get("doi_found"):
            sections.append("Published in peer-reviewed source.")

        return (
            " ".join(sections)
            if sections
            else "Limited methodological information available."
        )

    def _generate_evidence_section(
        self, similarity_result: Dict[str, Any], entailment_result: Dict[str, Any]
    ) -> str:
        sections = []

        # Similarity analysis
        similarity_score = similarity_result["similarity_score"]
        if similarity_score >= 0.8:
            sections.append("High semantic similarity between claim and findings.")
        elif similarity_score >= 0.6:
            sections.append("Moderate semantic similarity detected.")
        else:
            sections.append("Low semantic similarity with document content.")

        # Stance analysis
        stance = entailment_result["stance"]
        if stance == "supports":
            sections.append("Text analysis indicates supportive stance.")
        elif stance == "contradicts":
            sections.append("Text analysis indicates contradictory stance.")
        else:
            sections.append("Text analysis indicates neutral stance.")

        # Evidence count
        evidence_count = len(similarity_result["evidence_snippets"])
        sections.append(f"Found {evidence_count} relevant evidence passages.")

        return " ".join(sections)

    def _assess_overclaiming(
        self,
        user_claim: str,
        similarity_result: Dict[str, Any],
        confidence_score: float,
    ) -> str:
        # Analyze if the user claim goes beyond what the evidence supports

        # Check for absolute language in user claim
        absolute_terms = [
            "always",
            "never",
            "all",
            "none",
            "completely",
            "totally",
            "definitely",
            "certainly",
        ]
        has_absolute_language = any(
            term in user_claim.lower() for term in absolute_terms
        )

        # Check confidence vs similarity
        similarity_score = similarity_result["similarity_score"]

        if has_absolute_language and similarity_score < 0.7:
            return "Caution: Your claim uses absolute language that may not be fully supported by the evidence."
        elif confidence_score < 0.5:
            return (
                "The evidence provides limited support for strong claims in this area."
            )
        elif similarity_score < 0.4:
            return (
                "Your specific claim differs substantially from the study's findings."
            )
        else:
            return "No significant overclaiming detected based on available evidence."
