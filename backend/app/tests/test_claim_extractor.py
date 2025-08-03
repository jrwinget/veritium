import pytest
from app.services.claim_extractor import ClaimExtractor

@pytest.fixture
def claim_extractor():
    return ClaimExtractor()

class TestClaimExtractor:
    @pytest.mark.asyncio
    async def test_extract_claims(self, claim_extractor):
        text = """
        We conclude that regular exercise significantly reduces cardiovascular disease risk.
        Our findings suggest that meditation improves mental health outcomes.
        Therefore, we recommend implementing these interventions in clinical practice.
        """
        claims = await claim_extractor.extract_claims(text)
        assert len(claims) > 0
        assert any("exercise" in claim.lower() for claim in claims)
        assert any("meditation" in claim.lower() for claim in claims)

    def test_clean_claim(self, claim_extractor):
        dirty_claim = "   that    exercise    is    beneficial   "
        clean_claim = claim_extractor._clean_claim(dirty_claim)
        assert clean_claim == "exercise is beneficial"

    def test_is_valid_claim(self, claim_extractor):
        # Valid claim
        valid_claim = "Exercise significantly reduces cardiovascular disease risk"
        assert claim_extractor._is_valid_claim(valid_claim) == True
        
        # Too short
        short_claim = "Exercise good"
        assert claim_extractor._is_valid_claim(short_claim) == False
        
        # Citation only
        citation_claim = "[Smith et al., 2020]"
        assert claim_extractor._is_valid_claim(citation_claim) == False

    def test_are_similar_claims(self, claim_extractor):
        claim1 = "Exercise reduces heart disease risk"
        claim2 = "Physical activity decreases cardiovascular risk"
        claim3 = "Meditation improves mental health"
        
        # Should be somewhat similar (different words, same concept)
        similarity1 = claim_extractor._are_similar_claims(claim1, claim2)
        
        # Should not be similar (different topics)
        similarity2 = claim_extractor._are_similar_claims(claim1, claim3)
        
        assert similarity2 == False  # Different topics

    @pytest.mark.asyncio
    async def test_analyze_method_quality_indicators(self, claim_extractor):
        text = """
        Methods: We conducted a randomized controlled trial with n = 500 participants.
        Statistical analysis was performed using ANOVA with p < 0.05 significance level.
        """
        indicators = await claim_extractor.analyze_method_quality_indicators(text)
        
        assert indicators['sample_size'] == 500
        assert indicators['has_statistics'] == True
        assert len(indicators['p_values']) > 0