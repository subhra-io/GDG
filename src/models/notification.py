"""Notification Model"""
from sqlalchemy import Column, String, Boolean, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from src.core.database import Base


class Notification(Base):
    """Notification sent to users"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    violation_id = Column(UUID(as_uuid=True), ForeignKey("violations.id"), nullable=True)
    alert_rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.id"), nullable=True)
    
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # violation, review, system
    channel = Column(String(50), nullable=False)  # email, slack, in_app
    
    status = Column(String(50), default="pending")  # pending, sent, failed
    is_read = Column(Boolean, default=False)
    
    # Additional metadata as JSON
    notification_metadata = Column(JSONB)
    
    sent_at = Column(TIMESTAMP)
    read_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "violation_id": str(self.violation_id) if self.violation_id else None,
            "alert_rule_id": str(self.alert_rule_id) if self.alert_rule_id else None,
            "title": self.title,
            "message": self.message,
            "notification_type": self.notification_type,
            "channel": self.channel,
            "status": self.status,
            "is_read": self.is_read,
            "metadata": self.notification_metadata,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "read_at": self.read_at.isoformat() if self.read_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
