"""Rule dependency model for rule graph."""

from sqlalchemy import Column, String, Text, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from src.core.database import Base

class RuleDependency(Base):
    """Rule dependency for building rule graphs."""
    
    __tablename__ = "rule_dependencies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    depends_on_rule_id = Column(UUID(as_uuid=True), ForeignKey("compliance_rules.id", ondelete="CASCADE"), nullable=False)
    dependency_type = Column(String(50), nullable=False)  # 'requires', 'conflicts', 'extends'
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "rule_id": str(self.rule_id),
            "depends_on_rule_id": str(self.depends_on_rule_id),
            "dependency_type": self.dependency_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
