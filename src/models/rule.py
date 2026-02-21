"""Compliance rule models."""

from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from src.core.database import Base


class Severity(str, enum.Enum):
    """Rule severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ComplianceRule(Base):
    """Compliance rule extracted from policy documents."""
    
    __tablename__ = "compliance_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_document_id = Column(UUID(as_uuid=True), ForeignKey("policy_documents.id"), nullable=False)
    page_number = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    validation_logic = Column(JSONB, nullable=False)
    severity = Column(SQLEnum(Severity), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    confidence_score = Column(String(10), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Rule graph fields
    parent_rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id"), nullable=True)
    precedence = Column(String(10), default="0", nullable=True)
    
    # Relationships
    mappings = relationship("RuleMapping", back_populates="rule", cascade="all, delete-orphan")
    child_rules = relationship("ComplianceRule", backref="parent_rule", remote_side=[id])
    
    def __repr__(self):
        return f"<ComplianceRule(id={self.id}, severity={self.severity}, active={self.is_active})>"


class RuleMapping(Base):
    """Mapping of rules to database tables and columns."""
    
    __tablename__ = "rule_mappings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id"), nullable=False)
    table_name = Column(String(255), nullable=False)
    column_mappings = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    rule = relationship("ComplianceRule", back_populates="mappings")
    
    def __repr__(self):
        return f"<RuleMapping(id={self.id}, table={self.table_name})>"
