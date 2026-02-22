"""Alert Rule Model"""
from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.sql import func
import uuid
from src.core.database import Base


class AlertRule(Base):
    """Alert Rule for triggering notifications"""
    __tablename__ = "alert_rules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Trigger conditions as JSON
    # Example: {"severity": "critical", "rule_type": "sox", "risk_score_min": 80}
    trigger_condition = Column(JSONB, nullable=False)
    
    # Notification channels: email, slack, in_app
    notification_channels = Column(ARRAY(String), nullable=False)
    
    # Recipients as JSON
    # Example: {"emails": ["admin@company.com"], "slack_channels": ["#compliance"], "user_ids": ["uuid1", "uuid2"]}
    recipients = Column(JSONB, nullable=False)
    
    is_active = Column(Boolean, default=True)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "trigger_condition": self.trigger_condition,
            "notification_channels": self.notification_channels,
            "recipients": self.recipients,
            "is_active": self.is_active,
            "created_by": str(self.created_by) if self.created_by else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
