"""OpenAI LLM client implementation."""

import time
from openai import OpenAI
from typing import Optional

from .base import LLMClient, LLMResponse, LLMMetrics
from src.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIClient(LLMClient):
    """OpenAI API client."""
    
    # Pricing per 1K tokens (approximate)
    PRICING = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
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
        """Generate completion using OpenAI."""
        start_time = time.time()
        
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            response_time_ms = (time.time() - start_time) * 1000
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Calculate cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            pricing = self.PRICING.get(self.model, self.PRICING["gpt-4"])
            cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
            
            # Update metrics
            self._total_requests += 1
            self._total_tokens += tokens_used
            self._total_cost += cost
            self._total_response_time += response_time_ms
            
            logger.info(
                "OpenAI completion successful",
                model=self.model,
                tokens=tokens_used,
                cost=f"${cost:.4f}",
                response_time_ms=f"{response_time_ms:.2f}"
            )
            
            return LLMResponse(
                content=content,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
                provider="openai",
                model=self.model,
                cost_estimate=cost
            )
            
        except Exception as e:
            self._error_count += 1
            logger.error(f"OpenAI completion failed: {e}")
            raise
    
    def get_metrics(self) -> LLMMetrics:
        """Get usage metrics."""
        avg_response_time = (
            self._total_response_time / self._total_requests
            if self._total_requests > 0
            else 0.0
        )
        
        return LLMMetrics(
            provider="openai",
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
