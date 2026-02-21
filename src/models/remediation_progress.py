"""Remediation progress tracking models."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from src.core.database import Base


class RemediationProgress(Base):
    """Track remediation checklist progress."""
    
    __tablename__ = "remediation_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    step_index = Column(Integer, nullable=False)
    step_description = Column(Text, nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    completed_at = Column(DateTime, nullable=True)
    completed_by = Column(String(255), nullable=True)
    
    # Relationships
    violation = relationship("Violation", back_populates="remediation_progress")
    
    def __repr__(self):
        return f"<RemediationProgress(id={self.id}, violation_id={self.violation_id}, completed={self.completed})>"
