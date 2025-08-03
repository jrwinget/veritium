import re
from typing import List, Dict, Any


class QualityScorer:
    def __init__(self):
        self.quality_criteria = {
            "sample_size": {
                "weight": 0.15,
                "thresholds": {"excellent": 1000, "good": 100, "fair": 30, "poor": 10},
            },
            "methodology": {
                "weight": 0.25,
                "indicators": [
                    "randomized",
                    "random assignment",
                    "control group",
                    "placebo",
                    "double blind",
                    "single blind",
                    "systematic",
                    "meta-analysis",
                ],
            },
            "statistical_rigor": {
                "weight": 0.20,
                "indicators": [
                    "confidence interval",
                    "significance test",
                    "p-value",
                    "statistical power",
                    "effect size",
                    "regression",
                ],
            },
            "peer_review": {
                "weight": 0.15,
                "indicators": ["journal", "published", "peer review", "doi"],
            },
            "reproducibility": {
                "weight": 0.10,
                "indicators": [
                    "data availability",
                    "code availability",
                    "replication",
                    "supplementary material",
                    "methodology section",
                ],
            },
            "transparency": {
                "weight": 0.15,
                "indicators": [
                    "limitation",
                    "conflict of interest",
                    "funding",
                    "author contribution",
                    "acknowledgment",
                ],
            },
        }

    async def calculate_score(self, text: str, claims: List[str]) -> float:
        scores = {}

        # Sample size assessment
        scores["sample_size"] = self._assess_sample_size(text)

        # Methodology assessment
        scores["methodology"] = self._assess_methodology(text)

        # Statistical rigor assessment
        scores["statistical_rigor"] = self._assess_statistical_rigor(text)

        # Peer review indicators
        scores["peer_review"] = self._assess_peer_review(text)

        # Reproducibility indicators
        scores["reproducibility"] = self._assess_reproducibility(text)

        # Transparency indicators
        scores["transparency"] = self._assess_transparency(text)

        # Calculate weighted total score
        total_score = 0.0
        for criterion, weight in [
            (k, v["weight"]) for k, v in self.quality_criteria.items()
        ]:
            total_score += scores.get(criterion, 0.0) * weight

        # Normalize to 0-1 range
        return min(max(total_score, 0.0), 1.0)

    def _assess_sample_size(self, text: str) -> float:
        # Extract sample size from text
        patterns = [
            r"(?i)n\s*=\s*(\d+)",
            r"(?i)sample size\s*(?:of|was|is)?\s*(\d+)",
            r"(?i)(\d+)\s*participants",
            r"(?i)(\d+)\s*subjects",
            r"(?i)study\s*included\s*(\d+)",
        ]

        sample_sizes = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    size = int(match)
                    if 5 <= size <= 1000000:  # Reasonable range
                        sample_sizes.append(size)
                except ValueError:
                    continue

        if not sample_sizes:
            return 0.1  # Very low score if no sample size found

        max_sample_size = max(sample_sizes)
        thresholds = self.quality_criteria["sample_size"]["thresholds"]

        if max_sample_size >= thresholds["excellent"]:
            return 1.0
        elif max_sample_size >= thresholds["good"]:
            return 0.8
        elif max_sample_size >= thresholds["fair"]:
            return 0.6
        elif max_sample_size >= thresholds["poor"]:
            return 0.4
        else:
            return 0.2

    def _assess_methodology(self, text: str) -> float:
        indicators = self.quality_criteria["methodology"]["indicators"]
        found_indicators = 0

        for indicator in indicators:
            if re.search(rf"\b{re.escape(indicator)}\b", text, re.IGNORECASE):
                found_indicators += 1

        # Check for specific high-quality study types
        high_quality_types = [
            "randomized controlled trial",
            "rct",
            "systematic review",
            "meta-analysis",
            "longitudinal study",
            "cohort study",
        ]

        for study_type in high_quality_types:
            if re.search(rf"\b{re.escape(study_type)}\b", text, re.IGNORECASE):
                found_indicators += 2  # Bonus for high-quality study types

        # Score based on found indicators
        max_possible = len(indicators) + 4  # 4 bonus points possible
        score = min(found_indicators / max_possible, 1.0)

        return score

    def _assess_statistical_rigor(self, text: str) -> float:
        indicators = self.quality_criteria["statistical_rigor"]["indicators"]
        found_indicators = 0

        for indicator in indicators:
            if re.search(rf"\b{re.escape(indicator)}\b", text, re.IGNORECASE):
                found_indicators += 1

        # Look for specific statistical tests
        statistical_tests = [
            "t-test",
            "anova",
            "chi-square",
            "regression",
            "correlation",
            "mann-whitney",
            "kruskal-wallis",
            "wilcoxon",
        ]

        for test in statistical_tests:
            if re.search(rf"\b{re.escape(test)}\b", text, re.IGNORECASE):
                found_indicators += 1

        # Check for p-values and effect sizes
        if re.search(r"p\s*[<>=]\s*0\.\d+", text, re.IGNORECASE):
            found_indicators += 1

        if re.search(r"(?i)(?:cohen|effect size|eta|r\s*=)", text):
            found_indicators += 1

        # Score based on found indicators
        max_possible = len(indicators) + len(statistical_tests) + 2
        score = min(found_indicators / max_possible, 1.0)

        return score

    def _assess_peer_review(self, text: str) -> float:
        indicators = self.quality_criteria["peer_review"]["indicators"]
        score = 0.0

        # Check for journal publication indicators
        if re.search(r"(?i)\b(?:journal|published in|doi)\b", text):
            score += 0.5

        # Check for DOI pattern
        if re.search(r"doi\s*:\s*10\.\d+", text, re.IGNORECASE):
            score += 0.3

        # Check for citation format indicators
        if re.search(r"\(\d{4}\)", text):  # Year in parentheses
            score += 0.2

        return min(score, 1.0)

    def _assess_reproducibility(self, text: str) -> float:
        indicators = self.quality_criteria["reproducibility"]["indicators"]
        found_indicators = 0

        for indicator in indicators:
            if re.search(rf"\b{re.escape(indicator)}\b", text, re.IGNORECASE):
                found_indicators += 1

        # Check for specific reproducibility elements
        reproducibility_elements = [
            "github",
            "repository",
            "supplementary",
            "appendix",
            "raw data",
            "analysis code",
            "protocol",
        ]

        for element in reproducibility_elements:
            if re.search(rf"\b{re.escape(element)}\b", text, re.IGNORECASE):
                found_indicators += 1

        max_possible = len(indicators) + len(reproducibility_elements)
        score = min(found_indicators / max_possible, 1.0)

        return score

    def _assess_transparency(self, text: str) -> float:
        indicators = self.quality_criteria["transparency"]["indicators"]
        found_indicators = 0

        for indicator in indicators:
            if re.search(rf"\b{re.escape(indicator)}\b", text, re.IGNORECASE):
                found_indicators += 1

        # Check for specific transparency elements
        transparency_elements = [
            "ethical approval",
            "institutional review board",
            "irb",
            "consent",
            "ethics committee",
            "declaration",
        ]

        for element in transparency_elements:
            if re.search(rf"\b{re.escape(element)}\b", text, re.IGNORECASE):
                found_indicators += 1

        max_possible = len(indicators) + len(transparency_elements)
        score = min(found_indicators / max_possible, 1.0)

        return score

    async def get_detailed_assessment(
        self, text: str, claims: List[str]
    ) -> Dict[str, Any]:
        # Return detailed breakdown of quality assessment
        assessment = {}

        assessment["sample_size"] = {
            "score": self._assess_sample_size(text),
            "details": self._get_sample_size_details(text),
        }

        assessment["methodology"] = {
            "score": self._assess_methodology(text),
            "details": self._get_methodology_details(text),
        }

        assessment["statistical_rigor"] = {
            "score": self._assess_statistical_rigor(text),
            "details": self._get_statistical_details(text),
        }

        assessment["peer_review"] = {
            "score": self._assess_peer_review(text),
            "details": self._get_peer_review_details(text),
        }

        assessment["reproducibility"] = {
            "score": self._assess_reproducibility(text),
            "details": self._get_reproducibility_details(text),
        }

        assessment["transparency"] = {
            "score": self._assess_transparency(text),
            "details": self._get_transparency_details(text),
        }

        # Overall score
        total_score = await self.calculate_score(text, claims)
        assessment["overall_score"] = total_score

        return assessment

    def _get_sample_size_details(self, text: str) -> Dict[str, Any]:
        # Extract sample size details
        patterns = [
            r"(?i)n\s*=\s*(\d+)",
            r"(?i)sample size\s*(?:of|was|is)?\s*(\d+)",
            r"(?i)(\d+)\s*participants",
        ]

        sample_sizes = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            sample_sizes.extend([int(m) for m in matches if m.isdigit()])

        return {
            "sample_sizes_found": sample_sizes,
            "max_sample_size": max(sample_sizes) if sample_sizes else None,
        }

    def _get_methodology_details(self, text: str) -> Dict[str, Any]:
        indicators = self.quality_criteria["methodology"]["indicators"]
        found = []

        for indicator in indicators:
            if re.search(rf"\b{re.escape(indicator)}\b", text, re.IGNORECASE):
                found.append(indicator)

        return {"indicators_found": found}

    def _get_statistical_details(self, text: str) -> Dict[str, Any]:
        p_values = re.findall(r"p\s*[<>=]\s*(0\.\d+)", text, re.IGNORECASE)
        return {"p_values_found": p_values}

    def _get_peer_review_details(self, text: str) -> Dict[str, Any]:
        doi_match = re.search(r"doi\s*:\s*(10\.\d+/\S+)", text, re.IGNORECASE)
        return {"doi_found": doi_match.group(1) if doi_match else None}

    def _get_reproducibility_details(self, text: str) -> Dict[str, Any]:
        return {"has_methodology_section": bool(re.search(r"(?i)\bmethods?\b", text))}

    def _get_transparency_details(self, text: str) -> Dict[str, Any]:
        return {"mentions_limitations": bool(re.search(r"(?i)\blimitations?\b", text))}
