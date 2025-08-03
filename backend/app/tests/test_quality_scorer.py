import pytest
from app.services.quality_scorer import QualityScorer


@pytest.fixture
def quality_scorer():
    return QualityScorer()


class TestQualityScorer:
    @pytest.mark.asyncio
    async def test_calculate_score(self, quality_scorer):
        text = """
        Methods: We conducted a randomized controlled trial with 1000 participants.
        Statistical analysis included t-tests and confidence intervals (p < 0.05).
        This study was published in Nature and peer-reviewed.
        Data is available in supplementary materials with full methodology.
        Authors declare no conflicts of interest and acknowledge funding sources.
        """
        claims = ["Exercise reduces cardiovascular disease risk"]

        score = await quality_scorer.calculate_score(text, claims)
        assert 0.0 <= score <= 1.0
        assert score > 0.5  # Should be relatively high given the good indicators

    def test_assess_sample_size(self, quality_scorer):
        # Large sample size
        text_large = "We studied n = 2000 participants in this trial"
        score_large = quality_scorer._assess_sample_size(text_large)
        assert score_large >= 0.8

        # Small sample size
        text_small = "We studied n = 15 participants in this trial"
        score_small = quality_scorer._assess_sample_size(text_small)
        assert score_small < 0.5

        # No sample size
        text_none = "We conducted a study with some participants"
        score_none = quality_scorer._assess_sample_size(text_none)
        assert score_none == 0.1

    def test_assess_methodology(self, quality_scorer):
        # High-quality methodology
        text_high = """
        This randomized controlled trial used double-blind methodology
        with proper control group and systematic randomization procedures.
        """
        score_high = quality_scorer._assess_methodology(text_high)
        assert score_high > 0.3

        # Low-quality methodology
        text_low = "We conducted a simple observational study"
        score_low = quality_scorer._assess_methodology(text_low)
        assert score_low < score_high

    def test_assess_statistical_rigor(self, quality_scorer):
        text = """
        Statistical analysis included t-tests, ANOVA, and regression analysis.
        We report p-values, confidence intervals, and effect sizes.
        Significance level was set at p < 0.05.
        """
        score = quality_scorer._assess_statistical_rigor(text)
        assert score > 0.3

    @pytest.mark.asyncio
    async def test_get_detailed_assessment(self, quality_scorer):
        text = """
        Methods: Randomized controlled trial with n = 500 participants.
        Statistical analysis: t-tests with p < 0.05.
        Published in peer-reviewed journal with DOI: 10.1000/123456.
        """
        claims = ["Test claim"]

        assessment = await quality_scorer.get_detailed_assessment(text, claims)

        assert "sample_size" in assessment
        assert "methodology" in assessment
        assert "statistical_rigor" in assessment
        assert "overall_score" in assessment
        assert 0.0 <= assessment["overall_score"] <= 1.0
