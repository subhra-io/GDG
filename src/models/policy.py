"""Policy document model."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
import enum

from src.core.database import Base


class PolicyStatus(str, enum.Enum):
    """Policy document status."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class PolicyDocument(Base):
    """Policy document uploaded by users."""
    
    __tablename__ = "policy_documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename = Column(String(255), nullable=False)
    upload_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    file_size_bytes = Column(Integer, nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True)
    status = Column(SQLEnum(PolicyStatus), nullable=False, default=PolicyStatus.UPLOADED)
    extracted_text = Column(Text, nullable=True)
    document_metadata = Column(JSONB, nullable=True)  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    error_message = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<PolicyDocument(id={self.id}, filename={self.filename}, status={self.status})>"
