from typing import List, Optional, Dict, Any
import torch
from app.core.config import settings

class LLMService:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.enabled = settings.USE_LLM
    
    def _load_model(self):
        if not self.enabled:
            return
        
        if self.model is None:
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                
                model_name = settings.LLM_MODEL
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
                
                # Add padding token if not present
                if self.tokenizer.pad_token is None:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                    
            except Exception as e:
                print(f"Failed to load LLM model: {e}")
                self.enabled = False
                self.model = None
                self.tokenizer = None
    
    async def extract_claims_with_llm(self, text: str) -> List[str]:
        if not self.enabled:
            return []
        
        self._load_model()
        
        if self.model is None or self.tokenizer is None:
            return []
        
        try:
            # Construct prompt for claim extraction
            prompt = self._construct_claim_extraction_prompt(text)
            
            # Generate response
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract claims from response
            claims = self._parse_claims_from_response(response)
            
            return claims[:5]  # Limit to top 5 claims
            
        except Exception as e:
            print(f"LLM claim extraction failed: {e}")
            return []
    
    def _construct_claim_extraction_prompt(self, text: str) -> str:
        # Truncate text if too long
        max_text_length = 1000
        if len(text) > max_text_length:
            text = text[:max_text_length] + "..."
        
        prompt = f"""
Given the following scientific text, extract the main claims and conclusions. 
Focus on specific, factual statements about findings, results, or conclusions.

Text: {text}

Main claims and conclusions:
1."""
        
        return prompt
    
    def _parse_claims_from_response(self, response: str) -> List[str]:
        # Simple parsing of numbered claims
        claims = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            # Look for numbered claims
            if any(line.startswith(f"{i}.") for i in range(1, 10)):
                # Remove number and clean up
                claim = line.split('.', 1)[-1].strip()
                if len(claim) > 20 and len(claim) < 500:  # Reasonable length
                    claims.append(claim)
        
        return claims
    
    async def enhance_explanation(
        self, 
        base_explanation: str, 
        user_claim: str, 
        evidence: str
    ) -> str:
        if not self.enabled:
            return base_explanation
        
        self._load_model()
        
        if self.model is None or self.tokenizer is None:
            return base_explanation
        
        try:
            prompt = f"""
Improve this explanation of how scientific evidence relates to a user's claim.
Make it more detailed and educational while remaining accurate.

User's claim: {user_claim}

Current explanation: {base_explanation}

Evidence summary: {evidence[:300]}...

Improved explanation:"""
            
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 150,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract the improved explanation
            improved = response.split("Improved explanation:")[-1].strip()
            
            # Fallback to base explanation if generation failed
            if len(improved) < 50 or len(improved) > 1000:
                return base_explanation
            
            return improved
            
        except Exception as e:
            print(f"LLM explanation enhancement failed: {e}")
            return base_explanation
    
    async def assess_methodology_quality(self, text: str) -> Dict[str, Any]:
        if not self.enabled:
            return {}
        
        self._load_model()
        
        if self.model is None or self.tokenizer is None:
            return {}
        
        try:
            prompt = f"""
Analyze the methodology quality of this scientific text. 
Rate the study design, sample size, statistical methods, and overall rigor.

Text: {text[:800]}...

Methodology assessment:
Study design quality:"""
            
            inputs = self.tokenizer.encode(prompt, return_tensors="pt", max_length=512, truncation=True)
            
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=inputs.shape[1] + 100,
                    temperature=0.5,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id
                )
            
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Parse methodology assessment
            assessment = self._parse_methodology_assessment(response)
            
            return assessment
            
        except Exception as e:
            print(f"LLM methodology assessment failed: {e}")
            return {}
    
    def _parse_methodology_assessment(self, response: str) -> Dict[str, Any]:
        # Simple parsing of methodology assessment
        # In a production system, this would be more sophisticated
        
        assessment = {
            'llm_analysis': response.split("Methodology assessment:")[-1].strip()[:500],
            'confidence': 0.5  # Default confidence for LLM assessment
        }
        
        # Look for quality indicators in the response
        quality_keywords = ['excellent', 'good', 'poor', 'weak', 'strong', 'robust']
        found_keywords = [kw for kw in quality_keywords if kw in response.lower()]
        
        if found_keywords:
            assessment['quality_indicators'] = found_keywords
        
        return assessment