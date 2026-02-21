"""LLM client factory."""

from typing import Optional

from .base import LLMClient
from .openai_client import OpenAIClient
from .gemini_client import GeminiClient
from .router import LLMRouter
from src.config.settings import settings
from src.core.logging import get_logger

logger = get_logger(__name__)


def create_llm_router() -> LLMRouter:
    """
    Create LLM router with primary and fallback clients.
    
    Returns:
        LLMRouter configured based on settings
    """
    # Always create OpenAI client as it's required
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required")
    
    openai_client = OpenAIClient(
        api_key=settings.openai_api_key,
        model=settings.llm_model if settings.llm_provider == "openai" else "gpt-4"
    )
    
    # Create Gemini client if API key is available
    gemini_client: Optional[LLMClient] = None
    if settings.google_api_key:
        try:
            gemini_client = GeminiClient(
                api_key=settings.google_api_key,
                model="gemini-pro"
            )
            logger.info("Gemini client initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini client: {e}")
    
    # Determine primary and fallback based on settings
    if settings.llm_provider == "gemini" and gemini_client:
        primary = gemini_client
        fallback = openai_client
        logger.info("Using Gemini as primary, OpenAI as fallback")
    else:
        primary = openai_client
        fallback = gemini_client if gemini_client else openai_client
        logger.info("Using OpenAI as primary" + (", Gemini as fallback" if gemini_client else ""))
    
    return LLMRouter(primary=primary, fallback=fallback)


def create_llm_client(provider: str = "openai") -> LLMClient:
    """
    Create a specific LLM client.
    
    Args:
        provider: "openai" or "gemini"
        
    Returns:
        LLMClient instance
    """
    if provider == "openai":
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        return OpenAIClient(
            api_key=settings.openai_api_key,
            model=settings.llm_model
        )
    elif provider == "gemini":
        if not settings.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required")
        return GeminiClient(
            api_key=settings.google_api_key,
            model="gemini-pro"
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
