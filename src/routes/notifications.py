"""Notifications API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.services.notification_service import NotificationService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


class MarkAsReadRequest(BaseModel):
    """Mark as read request schema"""
    user_id: str


class MarkAllAsReadRequest(BaseModel):
    """Mark all as read request schema"""
    user_id: str


@router.get("/user/{user_id}")
async def get_user_notifications(
    user_id: str,
    unread_only: bool = False,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get notifications for a user"""
    try:
        service = NotificationService(db)
        notifications = service.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit
        )
        
        return {
            "notifications": notifications,
            "count": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting user notifications: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/unread-count")
async def get_unread_count(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get count of unread notifications"""
    try:
        service = NotificationService(db)
        count = service.get_unread_count(user_id)
        
        return {
            "unread_count": count
        }
        
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    request: MarkAsReadRequest,
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        service = NotificationService(db)
        success = service.mark_as_read(notification_id, request.user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        return {
            "message": "Notification marked as read",
            "notification_id": notification_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/mark-all-read")
async def mark_all_as_read(
    request: MarkAllAsReadRequest,
    db: Session = Depends(get_db)
):
    """Mark all notifications as read for a user"""
    try:
        service = NotificationService(db)
        count = service.mark_all_as_read(request.user_id)
        
        return {
            "message": f"Marked {count} notifications as read",
            "count": count
        }
        
    except Exception as e:
        logger.error(f"Error marking all as read: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_notification_history(
    user_id: Optional[str] = None,
    channel: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get notification history with filters"""
    try:
        from src.models.notification import Notification
        
        query = db.query(Notification)
        
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        if channel:
            query = query.filter(Notification.channel == channel)
        if status:
            query = query.filter(Notification.status == status)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
        
        return {
            "notifications": [n.to_dict() for n in notifications],
            "count": len(notifications)
        }
        
    except Exception as e:
        logger.error(f"Error getting notification history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_notification_statistics(
    user_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get notification statistics"""
    try:
        from src.models.notification import Notification
        from sqlalchemy import func
        
        query = db.query(Notification)
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        
        total = query.count()
        unread = query.filter(Notification.is_read == False).count()
        by_channel = db.query(
            Notification.channel,
            func.count(Notification.id)
        ).group_by(Notification.channel).all()
        
        by_type = db.query(
            Notification.notification_type,
            func.count(Notification.id)
        ).group_by(Notification.notification_type).all()
        
        return {
            "total": total,
            "unread": unread,
            "read": total - unread,
            "by_channel": {channel: count for channel, count in by_channel},
            "by_type": {ntype: count for ntype, count in by_type}
        }
        
    except Exception as e:
        logger.error(f"Error getting notification statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
