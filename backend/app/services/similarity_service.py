import numpy as np
from typing import List, Dict, Tuple, Any
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import re

class SimilarityService:
    def __init__(self):
        self.model = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=10000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def _load_model(self):
        if self.model is None:
            # Use a lightweight sentence transformer model
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except Exception:
                # Fallback to None if model loading fails
                self.model = None
    
    async def calculate_similarity(
        self, 
        user_claim: str, 
        document_claims: List[str], 
        document_content: str
    ) -> Dict[str, Any]:
        # Clean and prepare texts
        user_claim_clean = self._preprocess_text(user_claim)
        document_claims_clean = [self._preprocess_text(claim) for claim in document_claims]
        
        # Calculate semantic similarity using sentence transformers
        semantic_scores = await self._calculate_semantic_similarity(
            user_claim_clean, document_claims_clean
        )
        
        # Calculate keyword/lexical similarity
        lexical_scores = await self._calculate_lexical_similarity(
            user_claim_clean, document_claims_clean
        )
        
        # Find best matching evidence snippets from document content
        evidence_snippets = await self._find_evidence_snippets(
            user_claim_clean, document_content
        )
        
        # Combine scores
        combined_scores = []
        for i in range(len(document_claims_clean)):
            semantic_score = semantic_scores[i] if i < len(semantic_scores) else 0.0
            lexical_score = lexical_scores[i] if i < len(lexical_scores) else 0.0
            
            # Weighted combination (semantic more important)
            combined_score = 0.7 * semantic_score + 0.3 * lexical_score
            combined_scores.append(combined_score)
        
        # Get the best match
        best_score = max(combined_scores) if combined_scores else 0.0
        best_match_idx = combined_scores.index(best_score) if combined_scores else -1
        
        return {
            'similarity_score': best_score,
            'best_match_index': best_match_idx,
            'best_matching_claim': document_claims[best_match_idx] if best_match_idx >= 0 else "",
            'all_scores': combined_scores,
            'semantic_scores': semantic_scores,
            'lexical_scores': lexical_scores,
            'evidence_snippets': evidence_snippets[:5]  # Top 5 evidence snippets
        }
    
    async def _calculate_semantic_similarity(
        self, 
        user_claim: str, 
        document_claims: List[str]
    ) -> List[float]:
        self._load_model()
        
        if self.model is None or not document_claims:
            return [0.0] * len(document_claims)
        
        try:
            # Encode the user claim and document claims
            user_embedding = self.model.encode([user_claim])
            claim_embeddings = self.model.encode(document_claims)
            
            # Calculate cosine similarities
            similarities = cosine_similarity(user_embedding, claim_embeddings)[0]
            
            return similarities.tolist()
        except Exception:
            # Fallback to lexical similarity if semantic model fails
            return await self._calculate_lexical_similarity(user_claim, document_claims)
    
    async def _calculate_lexical_similarity(
        self, 
        user_claim: str, 
        document_claims: List[str]
    ) -> List[float]:
        if not document_claims:
            return []
        
        try:
            # Combine user claim with document claims for TF-IDF
            all_texts = [user_claim] + document_claims
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(all_texts)
            
            # Calculate similarities between user claim (index 0) and document claims
            user_vector = tfidf_matrix[0:1]
            claim_vectors = tfidf_matrix[1:]
            
            similarities = cosine_similarity(user_vector, claim_vectors)[0]
            
            return similarities.tolist()
        except Exception:
            # Simple word overlap fallback
            return [self._word_overlap_similarity(user_claim, claim) for claim in document_claims]
    
    def _word_overlap_similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    async def _find_evidence_snippets(
        self, 
        user_claim: str, 
        document_content: str
    ) -> List[Dict[str, Any]]:
        # Split document into sentences
        sentences = self._split_into_sentences(document_content)
        
        # Calculate similarity between user claim and each sentence
        sentence_scores = []
        
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 20:  # Skip very short sentences
                continue
            
            # Calculate similarity
            similarity = await self._calculate_sentence_similarity(user_claim, sentence)
            
            if similarity > 0.1:  # Only include relevant sentences
                sentence_scores.append({
                    'text': sentence.strip(),
                    'similarity': similarity,
                    'sentence_index': i,
                    'word_count': len(sentence.split())
                })
        
        # Sort by similarity and return top matches
        sentence_scores.sort(key=lambda x: x['similarity'], reverse=True)
        
        return sentence_scores[:10]  # Top 10 evidence snippets
    
    async def _calculate_sentence_similarity(self, claim: str, sentence: str) -> float:
        self._load_model()
        
        if self.model is not None:
            try:
                embeddings = self.model.encode([claim, sentence])
                similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
                return float(similarity)
            except Exception:
                pass
        
        # Fallback to word overlap
        return self._word_overlap_similarity(claim, sentence)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 10]
    
    def _preprocess_text(self, text: str) -> str:
        # Basic text preprocessing
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove citations [1], (Smith et al., 2020), etc.
        text = re.sub(r'\[.*?\]', '', text)
        text = re.sub(r'\(.*?\d{4}.*?\)', '', text)
        
        return text
    
    async def calculate_entailment_score(
        self, 
        user_claim: str, 
        evidence_text: str
    ) -> Dict[str, Any]:
        # Simple rule-based entailment detection
        # In a production system, you might use a dedicated NLI model
        
        user_claim_lower = user_claim.lower()
        evidence_lower = evidence_text.lower()
        
        # Look for contradiction indicators
        contradiction_indicators = [
            'not', 'no', 'never', 'none', 'neither', 'nor', 'cannot', 'unable',
            'failed', 'unsuccessful', 'ineffective', 'opposite', 'contrary',
            'however', 'but', 'although', 'despite', 'nevertheless'
        ]
        
        # Look for support indicators
        support_indicators = [
            'confirm', 'support', 'evidence', 'demonstrate', 'show', 'indicate',
            'suggest', 'prove', 'establish', 'validate', 'corroborate',
            'consistent', 'agree', 'align', 'match', 'correspond'
        ]
        
        # Count indicators
        contradiction_count = sum(1 for indicator in contradiction_indicators 
                                 if indicator in evidence_lower)
        support_count = sum(1 for indicator in support_indicators 
                           if indicator in evidence_lower)
        
        # Calculate scores
        if contradiction_count > support_count:
            stance = "contradicts"
            confidence = min(0.8, contradiction_count * 0.2)
        elif support_count > contradiction_count:
            stance = "supports"
            confidence = min(0.8, support_count * 0.2)
        else:
            stance = "neutral"
            confidence = 0.5
        
        return {
            'stance': stance,
            'entailment_score': confidence,
            'support_indicators': support_count,
            'contradiction_indicators': contradiction_count
        }