"""Notification Service - Orchestrates all notifications"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from src.models.notification import Notification
from src.models.alert_rule import AlertRule
from src.models.violation import Violation
from src.models.user import User
from src.services.email_service import EmailService
from src.services.slack_service import SlackService

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService()
        self.slack_service = SlackService()
    
    def check_and_send_alerts(self, violation: Violation) -> List[str]:
        """
        Check alert rules and send notifications for a violation
        
        Args:
            violation: Violation object
            
        Returns:
            List of notification IDs created
        """
        notification_ids = []
        
        # Get active alert rules
        alert_rules = self.db.query(AlertRule).filter(
            AlertRule.is_active == True
        ).all()
        
        for rule in alert_rules:
            if self._matches_trigger_condition(violation, rule.trigger_condition):
                logger.info(f"Violation {violation.id} matches alert rule {rule.name}")
                
                # Send notifications through configured channels
                for channel in rule.notification_channels:
                    notification_id = self._send_notification(
                        violation=violation,
                        alert_rule=rule,
                        channel=channel
                    )
                    if notification_id:
                        notification_ids.append(notification_id)
        
        return notification_ids
    
    def _matches_trigger_condition(
        self,
        violation: Violation,
        condition: Dict[str, Any]
    ) -> bool:
        """
        Check if violation matches trigger condition
        
        Args:
            violation: Violation object
            condition: Trigger condition dict
            
        Returns:
            True if matches, False otherwise
        """
        try:
            # Check severity
            if 'severity' in condition:
                if violation.severity != condition['severity']:
                    return False
            
            # Check risk score minimum
            if 'risk_score_min' in condition:
                if violation.risk_score < condition['risk_score_min']:
                    return False
            
            # Check risk score maximum
            if 'risk_score_max' in condition:
                if violation.risk_score > condition['risk_score_max']:
                    return False
            
            # Check rule type (if rule has a type field)
            if 'rule_type' in condition:
                # This would require adding a type field to ComplianceRule
                # For now, skip this check
                pass
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking trigger condition: {str(e)}")
            return False
    
    def _send_notification(
        self,
        violation: Violation,
        alert_rule: AlertRule,
        channel: str
    ) -> Optional[str]:
        """
        Send notification through specified channel
        
        Args:
            violation: Violation object
            alert_rule: AlertRule object
            channel: Notification channel (email, slack, in_app)
            
        Returns:
            Notification ID if created, None otherwise
        """
        try:
            violation_data = {
                'id': str(violation.id),
                'severity': violation.severity,
                'rule_name': violation.rule_name,
                'description': violation.description,
                'risk_score': violation.risk_score
            }
            
            # Get recipients
            recipients = alert_rule.recipients or {}
            
            # Send based on channel
            success = False
            if channel == 'email':
                emails = recipients.get('emails', [])
                if emails:
                    success = self.email_service.send_violation_alert(emails, violation_data)
            
            elif channel == 'slack':
                slack_channels = recipients.get('slack_channels', [])
                for slack_channel in slack_channels:
                    success = self.slack_service.send_violation_alert(
                        violation_data,
                        slack_channel
                    )
            
            elif channel == 'in_app':
                # Create in-app notifications for specified users
                user_ids = recipients.get('user_ids', [])
                for user_id in user_ids:
                    self._create_in_app_notification(
                        user_id=user_id,
                        violation=violation,
                        alert_rule=alert_rule
                    )
                success = True
            
            # Create notification record
            notification = Notification(
                violation_id=violation.id,
                alert_rule_id=alert_rule.id,
                title=f"{violation.severity.upper()} Violation Detected",
                message=f"{violation.rule_name}: {violation.description}",
                notification_type="violation",
                channel=channel,
                status="sent" if success else "failed",
                sent_at=datetime.utcnow() if success else None
            )
            
            self.db.add(notification)
            self.db.commit()
            
            return str(notification.id)
            
        except Exception as e:
            logger.error(f"Error sending notification: {str(e)}")
            self.db.rollback()
            return None
    
    def _create_in_app_notification(
        self,
        user_id: str,
        violation: Violation,
        alert_rule: AlertRule
    ) -> Optional[str]:
        """
        Create in-app notification for user
        
        Args:
            user_id: User ID
            violation: Violation object
            alert_rule: AlertRule object
            
        Returns:
            Notification ID if created
        """
        try:
            notification = Notification(
                user_id=user_id,
                violation_id=violation.id,
                alert_rule_id=alert_rule.id,
                title=f"{violation.severity.upper()} Violation Detected",
                message=f"{violation.rule_name}: {violation.description}",
                notification_type="violation",
                channel="in_app",
                status="sent",
                is_read=False,
                sent_at=datetime.utcnow(),
                notification_metadata={
                    'severity': violation.severity,
                    'risk_score': violation.risk_score
                }
            )
            
            self.db.add(notification)
            self.db.commit()
            
            return str(notification.id)
            
        except Exception as e:
            logger.error(f"Error creating in-app notification: {str(e)}")
            self.db.rollback()
            return None
    
    def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get notifications for a user
        
        Args:
            user_id: User ID
            unread_only: Only return unread notifications
            limit: Maximum number of notifications
            
        Returns:
            List of notification dicts
        """
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.channel == "in_app"
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(limit).all()
        
        return [n.to_dict() for n in notifications]
    
    def mark_as_read(self, notification_id: str, user_id: str) -> bool:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification ID
            user_id: User ID (for security)
            
        Returns:
            True if marked, False otherwise
        """
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if notification:
                notification.is_read = True
                notification.read_at = datetime.utcnow()
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            self.db.rollback()
            return False
    
    def mark_all_as_read(self, user_id: str) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Number of notifications marked
        """
        try:
            count = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.is_read == False
            ).update({
                'is_read': True,
                'read_at': datetime.utcnow()
            })
            
            self.db.commit()
            return count
            
        except Exception as e:
            logger.error(f"Error marking all as read: {str(e)}")
            self.db.rollback()
            return 0
    
    def get_unread_count(self, user_id: str) -> int:
        """
        Get count of unread notifications
        
        Args:
            user_id: User ID
            
        Returns:
            Count of unread notifications
        """
        return self.db.query(Notification).filter(
            Notification.user_id == user_id,
            Notification.channel == "in_app",
            Notification.is_read == False
        ).count()
    
    def send_review_notification(
        self,
        violation_id: str,
        reviewer_name: str,
        action: str,
        reason: str
    ) -> List[str]:
        """
        Send notification when a violation is reviewed
        
        Args:
            violation_id: Violation ID
            reviewer_name: Name of reviewer
            action: Review action
            reason: Review reason
            
        Returns:
            List of notification IDs created
        """
        notification_ids = []
        
        try:
            review_data = {
                'violation_id': violation_id,
                'reviewer_name': reviewer_name,
                'action': action,
                'reason': reason
            }
            
            # Send to configured channels (simplified - could be rule-based)
            # For now, just create in-app notifications for all admin users
            admins = self.db.query(User).filter(User.role == 'admin').all()
            
            for admin in admins:
                notification = Notification(
                    user_id=str(admin.id),
                    violation_id=violation_id,
                    title=f"Violation {action.replace('_', ' ').title()}",
                    message=f"{reviewer_name} {action.replace('_', ' ')} a violation: {reason}",
                    notification_type="review",
                    channel="in_app",
                    status="sent",
                    is_read=False,
                    sent_at=datetime.utcnow()
                )
                
                self.db.add(notification)
                notification_ids.append(str(notification.id))
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error sending review notification: {str(e)}")
            self.db.rollback()
        
        return notification_ids
