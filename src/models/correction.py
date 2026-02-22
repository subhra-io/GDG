"""Correction tracking models."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
import enum

from src.core.database import Base


class CorrectedDecision(str, enum.Enum):
    """Types of corrected decisions."""
    TRUE_POSITIVE = "true_positive"  # AI was correct
    FALSE_POSITIVE = "false_positive"  # AI was wrong
    NEEDS_REVIEW = "needs_review"  # Insufficient information


class Correction(Base):
    """Tracks human corrections to AI decisions."""
    
    __tablename__ = "corrections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id"), nullable=False)
    rule_name = Column(String(255), nullable=False)
    original_decision = Column(String(50), nullable=False, default="violation_detected")
    corrected_decision = Column(SQLEnum(CorrectedDecision), nullable=False)
    corrected_by = Column(String(255), nullable=False)  # User ID as string
    correction_reason = Column(Text, nullable=True)
    ai_confidence = Column(Float, nullable=True)
    severity = Column(String(20), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "violation_id": str(self.violation_id),
            "rule_id": str(self.rule_id),
            "rule_name": self.rule_name,
            "original_decision": self.original_decision,
            "corrected_decision": self.corrected_decision.value,
            "corrected_by": str(self.corrected_by),
            "correction_reason": self.correction_reason,
            "ai_confidence": self.ai_confidence,
            "severity": self.severity,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f"<Correction(id={self.id}, decision={self.corrected_decision})>"
