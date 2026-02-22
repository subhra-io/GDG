"""Prediction model for ML-based risk analysis."""

from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from src.core.database import Base


class Prediction(Base):
    """Model for storing violation predictions."""
    
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    record_id = Column(String, nullable=False, index=True)
    policy_id = Column(UUID(as_uuid=True), nullable=True)
    
    # Prediction results
    violation_probability = Column(Float, nullable=False)  # 0.0 to 1.0
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0
    risk_level = Column(String, nullable=False)  # 'low', 'medium', 'high', 'critical'
    
    # Risk analysis
    risk_factors = Column(JSON, nullable=False, default=list)  # List of risk factors
    recommendations = Column(JSON, nullable=False, default=list)  # Preventive recommendations
    
    # Metadata
    model_version = Column(String, nullable=False, default="1.0")
    predicted_at = Column(DateTime, default=datetime.utcnow)
    
    # Actual outcome (for feedback loop)
    actual_violation = Column(String, nullable=True)  # 'yes', 'no', null if not yet known
    prediction_accuracy = Column(Float, nullable=True)  # Calculated after actual outcome
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, record_id={self.record_id}, probability={self.violation_probability})>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            "id": str(self.id),
            "record_id": self.record_id,
            "policy_id": str(self.policy_id) if self.policy_id else None,
            "violation_probability": self.violation_probability,
            "confidence_score": self.confidence_score,
            "risk_level": self.risk_level,
            "risk_factors": self.risk_factors,
            "recommendations": self.recommendations,
            "model_version": self.model_version,
            "predicted_at": self.predicted_at.isoformat() if self.predicted_at else None,
            "actual_violation": self.actual_violation,
            "prediction_accuracy": self.prediction_accuracy
        }
