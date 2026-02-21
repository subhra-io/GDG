"""Google Gemini LLM client implementation."""

import time
import google.generativeai as genai
from typing import Optional

from .base import LLMClient, LLMResponse, LLMMetrics
from src.core.logging import get_logger

logger = get_logger(__name__)


class GeminiClient(LLMClient):
    """Google Gemini API client."""
    
    # Pricing per 1K tokens (approximate)
    PRICING = {
        "gemini-pro": {"input": 0.00025, "output": 0.0005},
        "gemini-1.5-pro": {"input": 0.00125, "output": 0.005},
    }
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google API key
            model: Model to use
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        
        # Metrics tracking
        self._total_requests = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        self._total_response_time = 0.0
        self._error_count = 0
    
    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """Generate completion using Gemini."""
        start_time = time.time()
        
        try:
            # Combine system message and prompt
            full_prompt = prompt
            if system_message:
                full_prompt = f"{system_message}\n\n{prompt}"
            
            # Configure generation
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            content = response.text
            
            # Estimate tokens (Gemini doesn't always provide token counts)
            # Rough estimate: 1 token ≈ 4 characters
            estimated_input_tokens = len(full_prompt) // 4
            estimated_output_tokens = len(content) // 4
            tokens_used = estimated_input_tokens + estimated_output_tokens
            
            # Calculate cost
            pricing = self.PRICING.get(self.model_name, self.PRICING["gemini-pro"])
            cost = (estimated_input_tokens / 1000 * pricing["input"]) + (estimated_output_tokens / 1000 * pricing["output"])
            
            # Update metrics
            self._total_requests += 1
            self._total_tokens += tokens_used
            self._total_cost += cost
            self._total_response_time += response_time_ms
            
            logger.info(
                "Gemini completion successful",
                model=self.model_name,
                tokens=tokens_used,
                cost=f"${cost:.4f}",
                response_time_ms=f"{response_time_ms:.2f}"
            )
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
                provider="gemini",
                model=self.model_name,
                cost_estimate=cost
            )
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"Gemini completion failed: {e}")
            raise
    
    def get_metrics(self) -> LLMMetrics:
        """Get usage metrics."""
        avg_response_time = (
            self._total_response_time / self._total_requests
            if self._total_requests > 0
            else 0.0
        )
        
        return LLMMetrics(
            provider="gemini",
            total_requests=self._total_requests,
            total_tokens=self._total_tokens,
            total_cost=self._total_cost,
            avg_response_time_ms=avg_response_time,
            error_count=self._error_count
        )
    
    def reset_metrics(self):
        """Reset usage metrics."""
        self._total_requests = 0
        self._total_tokens = 0
        self._total_cost = 0.0
        self._total_response_time = 0.0
        self._error_count = 0
