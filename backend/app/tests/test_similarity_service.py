import pytest
from app.services.similarity_service import SimilarityService

@pytest.fixture
def similarity_service():
    return SimilarityService()

class TestSimilarityService:
    @pytest.mark.asyncio
    async def test_calculate_similarity(self, similarity_service):
        user_claim = "Exercise reduces heart disease risk"
        document_claims = [
            "Physical activity decreases cardiovascular disease risk",
            "Meditation improves mental health outcomes",
            "Diet affects metabolic health"
        ]
        document_content = "Studies show that regular exercise is beneficial for heart health..."
        
        result = await similarity_service.calculate_similarity(
            user_claim, document_claims, document_content
        )
        
        assert 'similarity_score' in result
        assert 'best_match_index' in result
        assert 'evidence_snippets' in result
        assert 0.0 <= result['similarity_score'] <= 1.0
        assert result['best_match_index'] >= -1

    def test_word_overlap_similarity(self, similarity_service):
        text1 = "exercise reduces heart disease"
        text2 = "physical activity decreases heart problems"
        text3 = "meditation improves mental health"
        
        # Similar texts should have higher similarity
        sim1 = similarity_service._word_overlap_similarity(text1, text2)
        sim2 = similarity_service._word_overlap_similarity(text1, text3)
        
        assert sim1 > sim2  # First pair should be more similar

    def test_preprocess_text(self, similarity_service):
        messy_text = "This   text   has   [citations]   and   (Smith et al., 2020)   references"
        clean_text = similarity_service._preprocess_text(messy_text)
        
        assert "[citations]" not in clean_text
        assert "(Smith et al., 2020)" not in clean_text
        assert "   " not in clean_text

    @pytest.mark.asyncio
    async def test_calculate_entailment_score(self, similarity_service):
        # Supporting evidence
        claim = "Exercise reduces heart disease risk"
        supporting_evidence = "Studies confirm that regular exercise significantly decreases cardiovascular disease risk"
        
        result_support = await similarity_service.calculate_entailment_score(claim, supporting_evidence)
        assert result_support['stance'] in ['supports', 'contradicts', 'neutral']
        assert 0.0 <= result_support['entailment_score'] <= 1.0
        
        # Contradicting evidence
        contradicting_evidence = "Research shows that exercise does not reduce heart disease risk and may be harmful"
        result_contradict = await similarity_service.calculate_entailment_score(claim, contradicting_evidence)
        assert result_contradict['stance'] in ['supports', 'contradicts', 'neutral']

    def test_split_into_sentences(self, similarity_service):
        text = "This is sentence one. This is sentence two! Is this sentence three?"
        sentences = similarity_service._split_into_sentences(text)
        
        assert len(sentences) >= 2  # Should split into multiple sentences
        assert all(len(s.strip()) > 10 for s in sentences)  # Filter out short sentences