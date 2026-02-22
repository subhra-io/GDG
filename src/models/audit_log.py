"""Audit Log Model"""
from sqlalchemy import Column, String, Integer, Float, TIMESTAMP, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid
from src.core.database import Base


class AuditLog(Base):
    """Audit log for tracking all system events"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(TIMESTAMP, nullable=False, server_default=func.now())
    
    # Event classification
    event_type = Column(String(100), nullable=False)  # user_action, ai_decision, system_event
    action = Column(String(100), nullable=False)  # create, read, update, delete, execute
    
    # Resource information
    resource_type = Column(String(100))  # policy, violation, rule, review, etc.
    resource_id = Column(UUID(as_uuid=True))
    
    # User information
    user_id = Column(UUID(as_uuid=True))  # No foreign key constraint
    user_email = Column(String(255))
    ip_address = Column(String(50))
    user_agent = Column(Text)
    
    # Request information
    request_method = Column(String(10))  # GET, POST, PUT, DELETE
    request_path = Column(Text)
    request_body = Column(JSONB)
    
    # Response information
    response_status = Column(Integer)
    response_body = Column(JSONB)
    duration_ms = Column(Integer)  # Request duration in milliseconds
    
    # AI-specific fields
    ai_model = Column(String(100))  # gpt-4, gemini-pro, etc.
    ai_confidence = Column(Float)  # Confidence score for AI decisions
    
    # Additional metadata
    audit_metadata = Column(JSONB)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": str(self.id),
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "event_type": self.event_type,
            "action": self.action,
            "resource_type": self.resource_type,
            "resource_id": str(self.resource_id) if self.resource_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "user_email": self.user_email,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "request_method": self.request_method,
            "request_path": self.request_path,
            "request_body": self.request_body,
            "response_status": self.response_status,
            "response_body": self.response_body,
            "duration_ms": self.duration_ms,
            "ai_model": self.ai_model,
            "ai_confidence": self.ai_confidence,
            "metadata": self.audit_metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
