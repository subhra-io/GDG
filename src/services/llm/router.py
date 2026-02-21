"""LLM router with fallback support."""

from typing import Optional, Dict

from .base import LLMClient, LLMResponse, LLMMetrics
from src.core.logging import get_logger

logger = get_logger(__name__)


class LLMRouter:
    """Route requests to appropriate LLM with fallback."""
    
    def __init__(
        self,
        primary_client: LLMClient,
        fallback_client: LLMClient
    ):
        """
        Initialize LLM router.
        
        Args:
            primary_client: Primary LLM client
            fallback_client: Fallback LLM client
        """
        self.primary = primary_client
        self.fallback = fallback_client
    
    async def complete(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> LLMResponse:
        """
        Route to primary LLM, fallback on failure.
        
        Args:
            prompt: User prompt
            system_message: Optional system message
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            LLMResponse from primary or fallback
        """
        try:
            logger.info("Attempting primary LLM")
            return await self.primary.complete(
                prompt=prompt,
                system_message=system_message,
                temperature=temperature,
                max_tokens=max_tokens
            )
        except Exception as e:
            logger.warning(
                f"Primary LLM failed: {e}, using fallback",
                primary_provider=self.primary.get_metrics().provider
            )
            
            try:
                return await self.fallback.complete(
                    prompt=prompt,
                    system_message=system_message,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            except Exception as fallback_error:
                logger.error(f"Fallback LLM also failed: {fallback_error}")
                raise Exception(
                    f"Both primary and fallback LLMs failed. "
                    f"Primary: {str(e)}, Fallback: {str(fallback_error)}"
                )
    
    def get_all_metrics(self) -> Dict[str, LLMMetrics]:
        """
        Get metrics for all providers.
        
        Returns:
            Dictionary of provider metrics
        """
        return {
            "primary": self.primary.get_metrics(),
            "fallback": self.fallback.get_metrics()
        }
    
    def reset_all_metrics(self):
        """Reset metrics for all providers."""
        self.primary.reset_metrics()
        self.fallback.reset_metrics()
