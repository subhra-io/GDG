"""Base LLM client interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class LLMResponse:
    """Standardized LLM response."""
    content: str
    tokens_used: int
    response_time_ms: float
    provider: str
    model: str
    cost_estimate: float


@dataclass
class LLMMetrics:
    """LLM usage metrics."""
    provider: str
    total_requests: int
    total_tokens: int
    total_cost: float
    avg_response_time_ms: float
    error_count: int


class LLMClient(ABC):
    """Abstract LLM client interface."""
    
    @abstractmethod
    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """
        Generate completion.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse with content and metadata
        """
        pass
    
    @abstractmethod
    def get_metrics(self) -> LLMMetrics:
        """
        Get usage metrics.
        
        Returns:
            LLMMetrics with usage statistics
        """
        pass
    
    @abstractmethod
    def reset_metrics(self):
        """Reset usage metrics."""
        pass
