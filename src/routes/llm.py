"""LLM management routes."""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from src.services.llm.factory import create_llm_router, create_llm_client
from src.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/llm", tags=["llm"])

# Global router instance
_llm_router = None


def get_llm_router():
    """Get or create LLM router."""
    global _llm_router
    if _llm_router is None:
        _llm_router = create_llm_router()
    return _llm_router


@router.get("/metrics")
async def get_llm_metrics() -> Dict[str, Any]:
    """
    Get LLM usage metrics for all providers.
    
    Returns:
        Metrics for primary and fallback providers
    """
    try:
        router_instance = get_llm_router()
        metrics = router_instance.get_all_metrics()
        
        return {
            "primary": {
                "provider": metrics["primary"].provider,
                "total_requests": metrics["primary"].total_requests,
                "total_tokens": metrics["primary"].total_tokens,
                "total_cost": round(metrics["primary"].total_cost, 4),
                "avg_response_time_ms": round(metrics["primary"].avg_response_time_ms, 2),
                "error_count": metrics["primary"].error_count
            },
            "fallback": {
                "provider": metrics["fallback"].provider,
                "total_requests": metrics["fallback"].total_requests,
                "total_tokens": metrics["fallback"].total_tokens,
                "total_cost": round(metrics["fallback"].total_cost, 4),
                "avg_response_time_ms": round(metrics["fallback"].avg_response_time_ms, 2),
                "error_count": metrics["fallback"].error_count
            }
        }
    except Exception as e:
        logger.error(f"Failed to get LLM metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_llm_provider(provider: str) -> Dict[str, Any]:
    """
    Test a specific LLM provider.
    
    Args:
        provider: "openai" or "gemini"
        
    Returns:
        Test results with response time and status
    """
    try:
        client = create_llm_client(provider)
        
        # Test with a simple prompt
        response = await client.complete(
            prompt="Say 'Hello, I am working!' in exactly 5 words.",
            temperature=0.3,
            max_tokens=50
        )
        
        return {
            "status": "success",
            "provider": provider,
            "model": response.model,
            "response": response.content,
            "tokens_used": response.tokens_used,
            "response_time_ms": round(response.response_time_ms, 2),
            "cost_estimate": round(response.cost_estimate, 6)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"LLM test failed for {provider}: {e}")
        return {
            "status": "error",
            "provider": provider,
            "error": str(e)
        }


@router.post("/reset-metrics")
async def reset_llm_metrics() -> Dict[str, str]:
    """
    Reset LLM usage metrics.
    
    Returns:
        Success message
    """
    try:
        router_instance = get_llm_router()
        router_instance.reset_all_metrics()
        return {"message": "Metrics reset successfully"}
    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
