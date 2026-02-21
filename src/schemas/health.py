"""Health check schemas."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    postgres: str
    mongodb: str
    redis: str
