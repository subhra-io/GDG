"""Audit Service - Manages audit logging"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import csv
import io
from src.models.audit_log import AuditLog

logger = logging.getLogger(__name__)


class AuditService:
    """Service for managing audit logs"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_log(
        self,
        event_type: str,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_method: Optional[str] = None,
        request_path: Optional[str] = None,
        request_body: Optional[Dict] = None,
        response_status: Optional[int] = None,
        response_body: Optional[Dict] = None,
        duration_ms: Optional[int] = None,
        ai_model: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Create an audit log entry
        
        Args:
            event_type: Type of event (user_action, ai_decision, system_event)
            action: Action performed (create, read, update, delete, execute)
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            user_id: User who performed the action
            user_email: Email of user
            ip_address: IP address of request
            user_agent: User agent string
            request_method: HTTP method
            request_path: Request path
            request_body: Request body
            response_status: HTTP response status
            response_body: Response body
            duration_ms: Request duration
            ai_model: AI model used (for AI decisions)
            ai_confidence: Confidence score (for AI decisions)
            metadata: Additional metadata
            
        Returns:
            Audit log ID
        """
        try:
            audit_log = AuditLog(
                event_type=event_type,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id,
                user_email=user_email,
                ip_address=ip_address,
                user_agent=user_agent,
                request_method=request_method,
                request_path=request_path,
                request_body=request_body,
                response_status=response_status,
                response_body=response_body,
                duration_ms=duration_ms,
                ai_model=ai_model,
                ai_confidence=ai_confidence,
                audit_metadata=metadata
            )
            
            self.db.add(audit_log)
            self.db.commit()
            self.db.refresh(audit_log)
            
            return str(audit_log.id)
            
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            self.db.rollback()
            return None
    
    def get_logs(
        self,
        event_type: Optional[str] = None,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get audit logs with filters
        
        Args:
            event_type: Filter by event type
            action: Filter by action
            resource_type: Filter by resource type
            resource_id: Filter by resource ID
            user_id: Filter by user ID
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of logs
            offset: Offset for pagination
            
        Returns:
            List of audit log dicts
        """
        query = self.db.query(AuditLog)
        
        if event_type:
            query = query.filter(AuditLog.event_type == event_type)
        if action:
            query = query.filter(AuditLog.action == action)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if resource_id:
            query = query.filter(AuditLog.resource_id == resource_id)
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        logs = query.order_by(
            AuditLog.timestamp.desc()
        ).limit(limit).offset(offset).all()
        
        return [log.to_dict() for log in logs]
    
    def get_log_by_id(self, log_id: str) -> Optional[Dict[str, Any]]:
        """
        Get audit log by ID
        
        Args:
            log_id: Audit log ID
            
        Returns:
            Audit log dict or None
        """
        log = self.db.query(AuditLog).filter(AuditLog.id == log_id).first()
        return log.to_dict() if log else None
    
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get audit log statistics
        
        Args:
            start_date: Start date for statistics
            end_date: End date for statistics
            
        Returns:
            Statistics dict
        """
        from sqlalchemy import func
        
        query = self.db.query(AuditLog)
        
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)
        
        total = query.count()
        
        by_event_type = self.db.query(
            AuditLog.event_type,
            func.count(AuditLog.id)
        ).group_by(AuditLog.event_type).all()
        
        by_action = self.db.query(
            AuditLog.action,
            func.count(AuditLog.id)
        ).group_by(AuditLog.action).all()
        
        by_resource_type = self.db.query(
            AuditLog.resource_type,
            func.count(AuditLog.id)
        ).filter(AuditLog.resource_type.isnot(None)).group_by(
            AuditLog.resource_type
        ).all()
        
        return {
            "total": total,
            "by_event_type": {et: count for et, count in by_event_type},
            "by_action": {action: count for action, count in by_action},
            "by_resource_type": {rt: count for rt, count in by_resource_type}
        }
    
    def export_to_csv(
        self,
        event_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10000
    ) -> str:
        """
        Export audit logs to CSV
        
        Args:
            event_type: Filter by event type
            start_date: Filter by start date
            end_date: Filter by end date
            limit: Maximum number of logs
            
        Returns:
            CSV string
        """
        logs = self.get_logs(
            event_type=event_type,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            'timestamp', 'event_type', 'action', 'resource_type', 'resource_id',
            'user_email', 'ip_address', 'request_method', 'request_path',
            'response_status', 'duration_ms', 'ai_model', 'ai_confidence'
        ])
        
        writer.writeheader()
        for log in logs:
            writer.writerow({
                'timestamp': log.get('timestamp', ''),
                'event_type': log.get('event_type', ''),
                'action': log.get('action', ''),
                'resource_type': log.get('resource_type', ''),
                'resource_id': log.get('resource_id', ''),
                'user_email': log.get('user_email', ''),
                'ip_address': log.get('ip_address', ''),
                'request_method': log.get('request_method', ''),
                'request_path': log.get('request_path', ''),
                'response_status': log.get('response_status', ''),
                'duration_ms': log.get('duration_ms', ''),
                'ai_model': log.get('ai_model', ''),
                'ai_confidence': log.get('ai_confidence', '')
            })
        
        return output.getvalue()
    
    def log_user_action(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Helper method to log user actions
        
        Args:
            action: Action performed
            resource_type: Type of resource
            resource_id: ID of resource
            user_id: User ID
            user_email: User email
            metadata: Additional metadata
            
        Returns:
            Audit log ID
        """
        return self.create_log(
            event_type="user_action",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            metadata=metadata
        )
    
    def log_ai_decision(
        self,
        action: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        ai_model: Optional[str] = None,
        ai_confidence: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Helper method to log AI decisions
        
        Args:
            action: Action performed
            resource_type: Type of resource
            resource_id: ID of resource
            ai_model: AI model used
            ai_confidence: Confidence score
            metadata: Additional metadata
            
        Returns:
            Audit log ID
        """
        return self.create_log(
            event_type="ai_decision",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ai_model=ai_model,
            ai_confidence=ai_confidence,
            user_email="AI Agent",
            metadata=metadata
        )
    
    def log_system_event(
        self,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Helper method to log system events
        
        Args:
            action: Action performed
            resource_type: Type of resource
            resource_id: ID of resource
            metadata: Additional metadata
            
        Returns:
            Audit log ID
        """
        return self.create_log(
            event_type="system_event",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_email="System",
            metadata=metadata
        )
