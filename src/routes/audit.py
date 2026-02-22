"""Audit Trail API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from src.core.database import get_db
from src.services.audit_service import AuditService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("/logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get audit logs with filters"""
    try:
        service = AuditService(db)
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        logs = service.get_logs(
            event_type=event_type,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit,
            offset=offset
        )
        
        return {
            "logs": logs,
            "count": len(logs),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/logs/{log_id}")
async def get_audit_log(
    log_id: str,
    db: Session = Depends(get_db)
):
    """Get audit log by ID"""
    try:
        service = AuditService(db)
        log = service.get_log_by_id(log_id)
        
        if not log:
            raise HTTPException(status_code=404, detail="Audit log not found")
        
        return log
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audit log: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_audit_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get audit log statistics"""
    try:
        service = AuditService(db)
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        stats = service.get_statistics(
            start_date=start_dt,
            end_date=end_dt
        )
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting audit statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export/csv")
async def export_audit_logs_csv(
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 10000,
    db: Session = Depends(get_db)
):
    """Export audit logs to CSV"""
    try:
        service = AuditService(db)
        
        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None
        
        csv_data = service.export_to_csv(
            event_type=event_type,
            start_date=start_dt,
            end_date=end_dt,
            limit=limit
        )
        
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={
                "Content-Disposition": "attachment; filename=audit_logs.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error exporting audit logs: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/log/user-action")
async def log_user_action(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    user_email: Optional[str] = None,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Manually log a user action"""
    try:
        service = AuditService(db)
        log_id = service.log_user_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            metadata=metadata
        )
        
        return {
            "message": "User action logged",
            "log_id": log_id
        }
        
    except Exception as e:
        logger.error(f"Error logging user action: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/log/ai-decision")
async def log_ai_decision(
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    ai_model: Optional[str] = None,
    ai_confidence: Optional[float] = None,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Manually log an AI decision"""
    try:
        service = AuditService(db)
        log_id = service.log_ai_decision(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ai_model=ai_model,
            ai_confidence=ai_confidence,
            metadata=metadata
        )
        
        return {
            "message": "AI decision logged",
            "log_id": log_id
        }
        
    except Exception as e:
        logger.error(f"Error logging AI decision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/log/system-event")
async def log_system_event(
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    metadata: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Manually log a system event"""
    try:
        service = AuditService(db)
        log_id = service.log_system_event(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            metadata=metadata
        )
        
        return {
            "message": "System event logged",
            "log_id": log_id
        }
        
    except Exception as e:
        logger.error(f"Error logging system event: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
