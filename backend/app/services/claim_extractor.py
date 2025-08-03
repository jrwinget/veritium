import re
from typing import List, Dict, Any
from app.core.config import settings
from app.services.llm_service import LLMService


class ClaimExtractor:
    def __init__(self):
        self.llm_service = LLMService()
        # Patterns for identifying claims and conclusions
        self.conclusion_patterns = [
            r"(?i)(?:we conclude|in conclusion|our findings suggest|results indicate|evidence suggests|we found that|this study shows|our results demonstrate|the data indicate|findings reveal)(.+?)(?:\.|;|\n)",
            r"(?i)(?:therefore|thus|hence|consequently|in summary|to summarize)(.+?)(?:\.|;|\n)",
            r"(?i)(?:our study provides evidence|we provide evidence|evidence supports|results support)(.+?)(?:\.|;|\n)",
        ]

        self.claim_patterns = [
            r"(?i)(?:we hypothesize|we propose|we suggest|we argue|we claim|our hypothesis|we predict)(.+?)(?:\.|;|\n)",
            r"(?i)(?:it is likely|it is probable|we expect|we anticipate)(.+?)(?:\.|;|\n)",
            r"(?i)(?:the present study|this research|our investigation|this work) (?:shows|demonstrates|reveals|indicates)(.+?)(?:\.|;|\n)",
        ]

        # Method indicators for quality assessment
        self.method_indicators = [
            r"(?i)(?:sample size|n =|participants|subjects)",
            r"(?i)(?:randomized|random assignment|control group|placebo)",
            r"(?i)(?:statistical analysis|significance|p-value|confidence interval)",
            r"(?i)(?:methodology|methods|procedure|protocol)",
            r"(?i)(?:data collection|measurement|instrument|questionnaire)",
        ]

    async def extract_claims(self, text: str) -> List[str]:
        claims = []

        # Extract conclusions
        for pattern in self.conclusion_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                claim = self._clean_claim(match.group(1))
                if self._is_valid_claim(claim):
                    claims.append(claim)

        # Extract other claims/hypotheses
        for pattern in self.claim_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                claim = self._clean_claim(match.group(1))
                if self._is_valid_claim(claim):
                    claims.append(claim)

        # Extract claims from abstract and conclusion sections
        claims.extend(await self._extract_from_sections(text))

        # Try LLM-assisted extraction if enabled
        if settings.USE_LLM:
            llm_claims = await self.llm_service.extract_claims_with_llm(text)
            claims.extend(llm_claims)

        # Remove duplicates and rank by importance
        unique_claims = []
        for claim in claims:
            if not any(
                self._are_similar_claims(claim, existing) for existing in unique_claims
            ):
                unique_claims.append(claim)

        # Sort by length/importance (longer claims often more substantive)
        unique_claims.sort(key=len, reverse=True)

        return unique_claims[:10]  # Limit to top 10 claims

    async def _extract_from_sections(self, text: str) -> List[str]:
        claims = []

        # Extract from abstract
        abstract_match = re.search(
            r"(?i)abstract\s*[:\-]?\s*(.+?)(?=\n\s*\n|\n\s*(?:introduction|keywords|1\.))",
            text,
            re.DOTALL,
        )
        if abstract_match:
            abstract_text = abstract_match.group(1)
            claims.extend(self._extract_sentences_with_claims(abstract_text))

        # Extract from conclusion/discussion section
        conclusion_match = re.search(
            r"(?i)(?:conclusion|discussion|summary)\s*[:\-]?\s*(.+?)(?=\n\s*\n|\n\s*(?:references|acknowledgments|appendix))",
            text,
            re.DOTALL,
        )
        if conclusion_match:
            conclusion_text = conclusion_match.group(1)
            claims.extend(self._extract_sentences_with_claims(conclusion_text))

        return claims

    def _extract_sentences_with_claims(self, text: str) -> List[str]:
        # Split into sentences and identify those with claim indicators
        sentences = re.split(r"[.!?]+", text)
        claims = []

        claim_indicators = [
            "significant",
            "significantly",
            "correlation",
            "associated",
            "effect",
            "increased",
            "decreased",
            "higher",
            "lower",
            "improvement",
            "reduction",
            "evidence",
            "support",
            "indicate",
            "suggest",
            "demonstrate",
            "show",
            "result",
            "finding",
            "outcome",
            "impact",
            "influence",
            "relationship",
        ]

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Reasonable sentence length
                # Check if sentence contains claim indicators
                if any(indicator in sentence.lower() for indicator in claim_indicators):
                    claims.append(sentence)

        return claims

    def _clean_claim(self, claim: str) -> str:
        # Clean up extracted claim text
        claim = claim.strip()
        claim = re.sub(r"\s+", " ", claim)  # Normalize whitespace
        claim = re.sub(
            r"^(?:that|which|who|where|when)\s+", "", claim, flags=re.I
        )  # Remove leading conjunctions
        return claim

    def _is_valid_claim(self, claim: str) -> bool:
        # Filter out invalid or low-quality claims
        if len(claim) < 20 or len(claim) > 500:
            return False

        # Must contain some substantive words
        substantive_words = len([w for w in claim.split() if len(w) > 3])
        if substantive_words < 3:
            return False

        # Should not be just a citation or reference
        if re.match(r"^\s*[\[\(].*[\]\)]\s*$", claim):
            return False

        return True

    def _are_similar_claims(self, claim1: str, claim2: str) -> bool:
        # Simple similarity check to remove near-duplicates
        words1 = set(claim1.lower().split())
        words2 = set(claim2.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))

        # Jaccard similarity threshold
        similarity = intersection / union if union > 0 else 0
        return similarity > 0.6

    async def analyze_method_quality_indicators(self, text: str) -> Dict[str, Any]:
        # Analyze text for methodological quality indicators
        indicators_found = {}

        for i, pattern in enumerate(self.method_indicators):
            matches = re.findall(pattern, text, re.IGNORECASE)
            indicators_found[f"indicator_{i}"] = len(matches) > 0

        # Extract sample size if mentioned
        sample_size_match = re.search(
            r"(?i)(?:n\s*=\s*|sample size.*?|participants.*?)(\d+)", text
        )
        sample_size = int(sample_size_match.group(1)) if sample_size_match else None

        # Look for statistical significance mentions
        p_value_matches = re.findall(r"(?i)p\s*[<>=]\s*(0\.\d+)", text)
        has_statistics = len(p_value_matches) > 0

        return {
            "method_indicators": indicators_found,
            "sample_size": sample_size,
            "has_statistics": has_statistics,
            "p_values": p_value_matches,
        }
