"""API routes."""

from .policy import router as policy_router
from .violations import router as violations_router
from .dashboard import router as dashboard_router
from .data import router as data_router

__all__ = [
    "policy_router",
    "violations_router",
    "dashboard_router",
    "data_router",
]
