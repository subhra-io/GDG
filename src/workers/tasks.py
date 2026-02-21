"""Celery tasks for background processing."""

import structlog
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from src.workers.celery_app import celery_app
from src.core.database import get_db_session
from src.services.violation_detector import ViolationDetector
from src.models.job import MonitoringJob
from src.models.rule import ComplianceRule

logger = structlog.get_logger()


@celery_app.task(name="src.workers.tasks.continuous_monitoring_task", bind=True)
def continuous_monitoring_task(self) -> Dict[str, Any]:
    """
    Continuous monitoring task that scans for violations.
    Runs every 5 minutes via Celery Beat.
    """
    task_id = self.request.id
    logger.info("continuous_monitoring_started", task_id=task_id)
    
    db = next(get_db_session())
    job = None
    
    try:
        # Create monitoring job record
        job = MonitoringJob(
            job_type="continuous_monitoring",
            status="running",
            started_at=datetime.utcnow(),
            result={"task_id": task_id}
        )
        db.add(job)
        db.commit()
        
        # Check if there are active rules
        active_rules = db.query(ComplianceRule).filter(
            ComplianceRule.is_active == True
        ).count()
        
        if active_rules == 0:
            logger.info("no_active_rules", task_id=task_id)
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result = {
                "task_id": task_id,
                "message": "No active rules to monitor",
                "violations_found": 0
            }
            db.commit()
            return job.result
        
        # Run violation detection
        detector = ViolationDetector(db)
        result = detector.scan_all_records()
        
        # Update job with results
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.result = {
            "task_id": task_id,
            "violations_found": result.get("violations_created", 0),
            "records_scanned": result.get("records_scanned", 0),
            "rules_evaluated": result.get("rules_evaluated", 0),
            "scan_duration_seconds": (datetime.utcnow() - job.started_at).total_seconds()
        }
        db.commit()
        
        logger.info(
            "continuous_monitoring_completed",
            task_id=task_id,
            violations_found=result.get("violations_created", 0),
            records_scanned=result.get("records_scanned", 0)
        )
        
        return job.result
        
    except Exception as e:
        logger.error("continuous_monitoring_failed", task_id=task_id, error=str(e))
        
        if job:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            db.commit()
        
        raise
    
    finally:
        db.close()


@celery_app.task(name="src.workers.tasks.scan_violations_task", bind=True)
def scan_violations_task(self, policy_id: str = None) -> Dict[str, Any]:
    """
    Manual scan task triggered by user.
    Can scan all policies or a specific policy.
    """
    task_id = self.request.id
    logger.info("scan_violations_started", task_id=task_id, policy_id=policy_id)
    
    db = next(get_db_session())
    job = None
    
    try:
        # Create monitoring job record
        job = MonitoringJob(
            job_type="manual_scan",
            status="running",
            started_at=datetime.utcnow(),
            result={"task_id": task_id, "policy_id": policy_id}
        )
        db.add(job)
        db.commit()
        
        # Run violation detection
        detector = ViolationDetector(db)
        
        if policy_id:
            result = detector.scan_by_policy(policy_id)
        else:
            result = detector.scan_all_records()
        
        # Update job with results
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.result = {
            "task_id": task_id,
            "policy_id": policy_id,
            "violations_found": result.get("violations_created", 0),
            "records_scanned": result.get("records_scanned", 0),
            "rules_evaluated": result.get("rules_evaluated", 0),
            "scan_duration_seconds": (datetime.utcnow() - job.started_at).total_seconds()
        }
        db.commit()
        
        logger.info(
            "scan_violations_completed",
            task_id=task_id,
            violations_found=result.get("violations_created", 0)
        )
        
        return job.result
        
    except Exception as e:
        logger.error("scan_violations_failed", task_id=task_id, error=str(e))
        
        if job:
            job.status = "failed"
            job.completed_at = datetime.utcnow()
            job.error_message = str(e)
            db.commit()
        
        raise
    
    finally:
        db.close()


@celery_app.task(name="src.workers.tasks.cleanup_old_jobs_task")
def cleanup_old_jobs_task() -> Dict[str, Any]:
    """
    Cleanup old monitoring jobs (older than 30 days).
    Runs daily at 2 AM.
    """
    logger.info("cleanup_old_jobs_started")
    
    db = next(get_db_session())
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        deleted_count = db.query(MonitoringJob).filter(
            MonitoringJob.started_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info("cleanup_old_jobs_completed", deleted_count=deleted_count)
        
        return {
            "deleted_count": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error("cleanup_old_jobs_failed", error=str(e))
        raise
    
    finally:
        db.close()


@celery_app.task(name="src.workers.tasks.extract_rules_task", bind=True)
def extract_rules_task(self, policy_id: str) -> Dict[str, Any]:
    """
    Extract rules from policy document using AI.
    This is a long-running task that should run in background.
    """
    task_id = self.request.id
    logger.info("extract_rules_started", task_id=task_id, policy_id=policy_id)
    
    db = next(get_db_session())
    
    try:
        from src.services.rule_extractor import RuleExtractor
        from src.models.policy import PolicyDocument
        
        # Get policy document
        policy = db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")
        
        # Update policy status
        policy.status = "processing"
        db.commit()
        
        # Extract rules
        extractor = RuleExtractor(db)
        rules = extractor.extract_rules_from_policy(policy_id)
        
        # Update policy status
        policy.status = "processed"
        db.commit()
        
        logger.info(
            "extract_rules_completed",
            task_id=task_id,
            policy_id=policy_id,
            rules_extracted=len(rules)
        )
        
        return {
            "task_id": task_id,
            "policy_id": policy_id,
            "rules_extracted": len(rules),
            "status": "completed"
        }
        
    except Exception as e:
        logger.error("extract_rules_failed", task_id=task_id, error=str(e))
        
        # Update policy status to failed
        from src.models.policy import PolicyDocument
        policy = db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if policy:
            policy.status = "failed"
            policy.error_message = str(e)
            db.commit()
        
        raise
    
    finally:
        db.close()
