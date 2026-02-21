"""Monitoring job models."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
import enum

from src.core.database import Base


class JobStatus(str, enum.Enum):
    """Job status."""
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class MonitoringJob(Base):
    """Scheduled monitoring job."""
    
    __tablename__ = "monitoring_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_name = Column(String(255), nullable=False)
    schedule_config = Column(JSONB, nullable=False)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.SCHEDULED)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    executions = relationship("JobExecution", back_populates="job", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<MonitoringJob(id={self.id}, name={self.job_name}, status={self.status})>"


class JobExecution(Base):
    """Job execution record."""
    
    __tablename__ = "job_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("monitoring_jobs.id"), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    records_scanned = Column(Integer, nullable=True)
    violations_detected = Column(Integer, nullable=True)
    status = Column(SQLEnum(JobStatus), nullable=False, default=JobStatus.RUNNING)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    job = relationship("MonitoringJob", back_populates="executions")
    
    def __repr__(self):
        return f"<JobExecution(id={self.id}, status={self.status})>"
