"""Monitoring and background task management routes."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from src.core.database import get_db
from src.models.job import MonitoringJob
from src.workers.tasks import scan_violations_task, continuous_monitoring_task
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/monitoring", tags=["monitoring"])


class MonitoringStatusResponse(BaseModel):
    """Monitoring status response."""
    is_monitoring_active: bool
    last_scan_time: Optional[datetime]
    last_scan_status: Optional[str]
    violations_found_last_scan: Optional[int]
    records_scanned_last_scan: Optional[int]
    total_scans_today: int
    next_scheduled_scan: Optional[datetime]


class ScanTriggerResponse(BaseModel):
    """Scan trigger response."""
    task_id: str
    message: str
    status: str


class JobStatusResponse(BaseModel):
    """Job status response."""
    job_id: str
    job_type: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    result: Optional[dict]
    error_message: Optional[str]


@router.get("/status", response_model=MonitoringStatusResponse)
def get_monitoring_status(db: Session = Depends(get_db)):
    """
    Get current monitoring status.
    Shows last scan info and monitoring health.
    """
    # Get last completed scan
    last_scan = db.query(MonitoringJob).filter(
        MonitoringJob.job_type.in_(["continuous_monitoring", "manual_scan"]),
        MonitoringJob.status == "completed"
    ).order_by(MonitoringJob.completed_at.desc()).first()
    
    # Count scans today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    scans_today = db.query(MonitoringJob).filter(
        MonitoringJob.job_type.in_(["continuous_monitoring", "manual_scan"]),
        MonitoringJob.started_at >= today_start
    ).count()
    
    # Check if monitoring is active (scan in last 10 minutes)
    recent_scan = db.query(MonitoringJob).filter(
        MonitoringJob.job_type == "continuous_monitoring",
        MonitoringJob.started_at >= datetime.utcnow() - timedelta(minutes=10)
    ).first()
    
    is_active = recent_scan is not None
    
    # Calculate next scheduled scan (every 5 minutes)
    next_scan = None
    if last_scan and last_scan.completed_at:
        next_scan = last_scan.completed_at + timedelta(minutes=5)
    
    return MonitoringStatusResponse(
        is_monitoring_active=is_active,
        last_scan_time=last_scan.completed_at if last_scan else None,
        last_scan_status=last_scan.status if last_scan else None,
        violations_found_last_scan=last_scan.result.get("violations_found", 0) if last_scan and last_scan.result else None,
        records_scanned_last_scan=last_scan.result.get("records_scanned", 0) if last_scan and last_scan.result else None,
        total_scans_today=scans_today,
        next_scheduled_scan=next_scan
    )


@router.post("/scan", response_model=ScanTriggerResponse)
def trigger_scan(
    policy_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Trigger a manual violation scan.
    Can scan all policies or a specific policy.
    """
    try:
        # Trigger async task
        task = scan_violations_task.delay(policy_id=policy_id)
        
        return ScanTriggerResponse(
            task_id=task.id,
            message=f"Scan started for {'policy ' + policy_id if policy_id else 'all policies'}",
            status="queued"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger scan: {str(e)}")


@router.post("/scan/immediate", response_model=dict)
def trigger_immediate_monitoring():
    """
    Trigger immediate continuous monitoring (bypass schedule).
    Useful for testing or urgent scans.
    """
    try:
        task = continuous_monitoring_task.delay()
        
        return {
            "task_id": task.id,
            "message": "Immediate monitoring scan started",
            "status": "queued"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger monitoring: {str(e)}")


@router.get("/jobs", response_model=List[JobStatusResponse])
def get_monitoring_jobs(
    limit: int = 20,
    job_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get monitoring job history.
    Filter by job type and status.
    """
    query = db.query(MonitoringJob)
    
    if job_type:
        query = query.filter(MonitoringJob.job_type == job_type)
    
    if status:
        query = query.filter(MonitoringJob.status == status)
    
    jobs = query.order_by(MonitoringJob.started_at.desc()).limit(limit).all()
    
    return [
        JobStatusResponse(
            job_id=str(job.id),
            job_type=job.job_type,
            status=job.status,
            started_at=job.started_at,
            completed_at=job.completed_at,
            result=job.result,
            error_message=job.error_message
        )
        for job in jobs
    ]


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get status of a specific monitoring job.
    """
    job = db.query(MonitoringJob).filter(MonitoringJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobStatusResponse(
        job_id=str(job.id),
        job_type=job.job_type,
        status=job.status,
        started_at=job.started_at,
        completed_at=job.completed_at,
        result=job.result,
        error_message=job.error_message
    )


@router.get("/health")
def monitoring_health_check(db: Session = Depends(get_db)):
    """
    Health check for monitoring system.
    Checks if Celery workers are running and Redis is accessible.
    """
    from src.workers.celery_app import celery_app
    
    try:
        # Check Celery workers
        inspect = celery_app.control.inspect()
        active_workers = inspect.active()
        
        if not active_workers:
            return {
                "status": "unhealthy",
                "message": "No Celery workers running",
                "workers": 0
            }
        
        # Check recent scans
        recent_scan = db.query(MonitoringJob).filter(
            MonitoringJob.started_at >= datetime.utcnow() - timedelta(minutes=15)
        ).first()
        
        return {
            "status": "healthy",
            "message": "Monitoring system operational",
            "workers": len(active_workers),
            "last_scan": recent_scan.started_at.isoformat() if recent_scan else None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Health check failed: {str(e)}",
            "workers": 0
        }
