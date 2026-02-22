"""Alert Rules API Routes"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.core.database import get_db
from src.models.alert_rule import AlertRule
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertRuleCreate(BaseModel):
    """Alert rule creation schema"""
    name: str
    description: Optional[str] = None
    trigger_condition: dict
    notification_channels: List[str]
    recipients: dict
    is_active: bool = True
    created_by: Optional[str] = None


class AlertRuleUpdate(BaseModel):
    """Alert rule update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    trigger_condition: Optional[dict] = None
    notification_channels: Optional[List[str]] = None
    recipients: Optional[dict] = None
    is_active: Optional[bool] = None


@router.get("/rules")
async def get_alert_rules(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all alert rules"""
    try:
        query = db.query(AlertRule)
        
        if is_active is not None:
            query = query.filter(AlertRule.is_active == is_active)
        
        rules = query.order_by(AlertRule.created_at.desc()).all()
        
        return {
            "rules": [rule.to_dict() for rule in rules],
            "count": len(rules)
        }
        
    except Exception as e:
        logger.error(f"Error getting alert rules: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/{rule_id}")
async def get_alert_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """Get alert rule by ID"""
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        return rule.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert rule: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules")
async def create_alert_rule(
    rule_data: AlertRuleCreate,
    db: Session = Depends(get_db)
):
    """Create new alert rule"""
    try:
        rule = AlertRule(
            name=rule_data.name,
            description=rule_data.description,
            trigger_condition=rule_data.trigger_condition,
            notification_channels=rule_data.notification_channels,
            recipients=rule_data.recipients,
            is_active=rule_data.is_active,
            created_by=rule_data.created_by
        )
        
        db.add(rule)
        db.commit()
        db.refresh(rule)
        
        logger.info(f"Created alert rule: {rule.name}")
        
        return {
            "message": "Alert rule created successfully",
            "rule": rule.to_dict()
        }
        
    except Exception as e:
        logger.error(f"Error creating alert rule: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}")
async def update_alert_rule(
    rule_id: str,
    rule_data: AlertRuleUpdate,
    db: Session = Depends(get_db)
):
    """Update alert rule"""
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        # Update fields
        if rule_data.name is not None:
            rule.name = rule_data.name
        if rule_data.description is not None:
            rule.description = rule_data.description
        if rule_data.trigger_condition is not None:
            rule.trigger_condition = rule_data.trigger_condition
        if rule_data.notification_channels is not None:
            rule.notification_channels = rule_data.notification_channels
        if rule_data.recipients is not None:
            rule.recipients = rule_data.recipients
        if rule_data.is_active is not None:
            rule.is_active = rule_data.is_active
        
        db.commit()
        db.refresh(rule)
        
        logger.info(f"Updated alert rule: {rule.name}")
        
        return {
            "message": "Alert rule updated successfully",
            "rule": rule.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating alert rule: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}")
async def delete_alert_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """Delete alert rule"""
    try:
        rule = db.query(AlertRule).filter(AlertRule.id == rule_id).first()
        
        if not rule:
            raise HTTPException(status_code=404, detail="Alert rule not found")
        
        rule_name = rule.name
        db.delete(rule)
        db.commit()
        
        logger.info(f"Deleted alert rule: {rule_name}")
        
        return {
            "message": "Alert rule deleted successfully",
            "rule_id": rule_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting alert rule: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test")
async def test_alert(
    channel: str,
    recipient: str,
    db: Session = Depends(get_db)
):
    """Test alert notification"""
    try:
        from src.services.email_service import EmailService
        from src.services.slack_service import SlackService
        
        test_data = {
            'id': 'test-123',
            'severity': 'high',
            'rule_name': 'Test Rule',
            'description': 'This is a test notification',
            'risk_score': 85
        }
        
        success = False
        if channel == 'email':
            email_service = EmailService()
            success = email_service.send_violation_alert([recipient], test_data)
        elif channel == 'slack':
            slack_service = SlackService()
            success = slack_service.send_violation_alert(test_data, recipient)
        else:
            raise HTTPException(status_code=400, detail="Invalid channel")
        
        return {
            "message": "Test notification sent" if success else "Test notification failed",
            "success": success,
            "channel": channel,
            "recipient": recipient
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing alert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
