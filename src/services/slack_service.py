"""Slack Service for sending notifications"""
import requests
import logging
from typing import Optional
from src.config.settings import settings

logger = logging.getLogger(__name__)


class SlackService:
    """Service for sending Slack notifications"""
    
    def __init__(self):
        self.webhook_url = getattr(settings, 'SLACK_WEBHOOK_URL', None)
        self.enabled = getattr(settings, 'SLACK_ENABLED', False)
    
    def send_message(
        self,
        text: str,
        channel: Optional[str] = None,
        blocks: Optional[list] = None
    ) -> bool:
        """
        Send Slack message
        
        Args:
            text: Message text (fallback)
            channel: Optional channel override
            blocks: Optional Slack blocks for rich formatting
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Slack disabled. Would send: {text}")
            return True
        
        if not self.webhook_url:
            logger.warning("Slack webhook URL not configured")
            return False
        
        try:
            payload = {"text": text}
            
            if channel:
                payload["channel"] = channel
            
            if blocks:
                payload["blocks"] = blocks
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info("Slack message sent successfully")
                return True
            else:
                logger.error(f"Slack API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Slack message: {str(e)}")
            return False
    
    def send_violation_alert(
        self,
        violation_data: dict,
        channel: Optional[str] = None
    ) -> bool:
        """
        Send violation alert to Slack
        
        Args:
            violation_data: Violation information
            channel: Optional channel override
            
        Returns:
            True if sent successfully
        """
        severity = violation_data.get('severity', 'unknown')
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }.get(severity.lower(), '⚪')
        
        text = f"{severity_emoji} {severity.upper()} Violation Detected"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{severity_emoji} {severity.upper()} Violation Detected"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Violation ID:*\n{violation_data.get('id', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity.upper()}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Rule:*\n{violation_data.get('rule_name', 'N/A')}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Risk Score:*\n{violation_data.get('risk_score', 'N/A')}/100"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Description:*\n{violation_data.get('description', 'No description available')}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Review Violation"
                        },
                        "url": f"http://localhost:3000/violations/{violation_data.get('id', '')}",
                        "style": "primary"
                    }
                ]
            }
        ]
        
        return self.send_message(text, channel, blocks)
    
    def send_review_notification(
        self,
        review_data: dict,
        channel: Optional[str] = None
    ) -> bool:
        """
        Send review notification to Slack
        
        Args:
            review_data: Review information
            channel: Optional channel override
            
        Returns:
            True if sent successfully
        """
        action = review_data.get('action', 'reviewed')
        action_emoji = {
            'confirm': '✅',
            'dismiss': '❌',
            'request_more_info': '❓'
        }.get(action, '📝')
        
        text = f"{action_emoji} Violation {action.replace('_', ' ').title()}"
        
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{action_emoji} *Violation {action.replace('_', ' ').title()}*\n\n"
                            f"*Violation ID:* {review_data.get('violation_id', 'N/A')}\n"
                            f"*Reviewer:* {review_data.get('reviewer_name', 'N/A')}\n"
                            f"*Reason:* {review_data.get('reason', 'No reason provided')}"
                }
            }
        ]
        
        return self.send_message(text, channel, blocks)
