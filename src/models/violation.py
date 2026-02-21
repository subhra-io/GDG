"""Violation models."""

from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from src.core.database import Base


class ViolationStatus(str, enum.Enum):
    """Violation status."""
    PENDING_REVIEW = "pending_review"
    CONFIRMED = "confirmed"
    DISMISSED = "dismissed"
    RESOLVED = "resolved"


class ReviewAction(str, enum.Enum):
    """Review action types."""
    CONFIRM = "confirm"
    DISMISS = "dismiss"
    REQUEST_MORE_INFO = "request_more_info"


class Violation(Base):
    """Detected compliance violation."""
    
    __tablename__ = "violations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id"), nullable=False)
    record_identifier = Column(String(255), nullable=False)
    table_name = Column(String(255), nullable=False)
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(SQLEnum(ViolationStatus), nullable=False, default=ViolationStatus.PENDING_REVIEW)
    justification = Column(Text, nullable=False)
    record_snapshot = Column(JSONB, nullable=False)
    severity = Column(String(20), nullable=False)
    remediation_steps = Column(JSONB, nullable=True)
    
    # Relationships
    reviews = relationship("ViolationReview", back_populates="violation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Violation(id={self.id}, status={self.status}, severity={self.severity})>"


class ViolationReview(Base):
    """Human review of violations."""
    
    __tablename__ = "violation_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=False)
    reviewer_user_id = Column(String(255), nullable=False)
    action = Column(SQLEnum(ReviewAction), nullable=False)
    reason = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    violation = relationship("Violation", back_populates="reviews")
    
    def __repr__(self):
        return f"<ViolationReview(id={self.id}, action={self.action})>"
