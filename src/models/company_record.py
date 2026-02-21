"""Company record model for demo/testing."""

from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

from src.core.database import Base


class CompanyRecord(Base):
    """Sample company records for compliance checking (AML/Financial transactions)."""
    
    __tablename__ = "company_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Transaction fields (for AML dataset)
    transaction_id = Column(String(255), nullable=True, unique=True)
    timestamp = Column(DateTime, nullable=True)
    from_account = Column(String(255), nullable=True)
    to_account = Column(String(255), nullable=True)
    amount = Column(Float, nullable=True)
    transaction_type = Column(String(50), nullable=True)
    
    # Generic fields for flexibility
    record_type = Column(String(50), nullable=False, default="transaction")
    data = Column(JSONB, nullable=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CompanyRecord(id={self.id}, type={self.record_type})>"
