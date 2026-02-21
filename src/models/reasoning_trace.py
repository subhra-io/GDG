"""Reasoning trace models."""

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class ReasoningTrace(Base):
    """Reasoning trace for violation decision."""
    
    __tablename__ = "reasoning_traces"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False, unique=True)
    steps = Column(JSONB, nullable=False)  # List of reasoning steps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    violation = relationship("Violation", back_populates="reasoning_trace")
    
    def __repr__(self):
        return f"<ReasoningTrace(id={self.id}, violation_id={self.violation_id})>"
