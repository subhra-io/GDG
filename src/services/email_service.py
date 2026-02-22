"""Email Service for sending notifications"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from src.config.settings import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""
    
    def __init__(self):
        self.smtp_host = getattr(settings, 'SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_user = getattr(settings, 'SMTP_USER', None)
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', None)
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@policysentinel.com')
        self.enabled = getattr(settings, 'EMAIL_ENABLED', False)
    
    def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Send email notification
        
        Args:
            to_emails: List of recipient email addresses
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to_emails}: {subject}")
            return True
        
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(to_emails)
            
            # Add plain text part
            text_part = MIMEText(body, 'plain')
            msg.attach(text_part)
            
            # Add HTML part if provided
            if html_body:
                html_part = MIMEText(html_body, 'html')
                msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_violation_alert(
        self,
        to_emails: List[str],
        violation_data: dict
    ) -> bool:
        """
        Send violation alert email
        
        Args:
            to_emails: List of recipient emails
            violation_data: Violation information
            
        Returns:
            True if sent successfully
        """
        subject = f"🚨 {violation_data.get('severity', 'Unknown').upper()} Violation Detected"
        
        body = f"""
PolicySentinel Alert

A {violation_data.get('severity', 'unknown')} severity violation has been detected.

Violation ID: {violation_data.get('id', 'N/A')}
Rule: {violation_data.get('rule_name', 'N/A')}
Severity: {violation_data.get('severity', 'N/A')}
Risk Score: {violation_data.get('risk_score', 'N/A')}/100

Description:
{violation_data.get('description', 'No description available')}

Please review this violation in the PolicySentinel dashboard.

---
PolicySentinel - AI-Powered Compliance Monitoring
        """
        
        html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #dc2626;">🚨 {violation_data.get('severity', 'Unknown').upper()} Violation Detected</h2>
        
        <div style="background: #f3f4f6; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Violation ID:</strong> {violation_data.get('id', 'N/A')}</p>
            <p><strong>Rule:</strong> {violation_data.get('rule_name', 'N/A')}</p>
            <p><strong>Severity:</strong> <span style="color: #dc2626;">{violation_data.get('severity', 'N/A')}</span></p>
            <p><strong>Risk Score:</strong> {violation_data.get('risk_score', 'N/A')}/100</p>
        </div>
        
        <div style="margin: 20px 0;">
            <h3>Description:</h3>
            <p>{violation_data.get('description', 'No description available')}</p>
        </div>
        
        <div style="margin: 30px 0;">
            <a href="http://localhost:3000/violations/{violation_data.get('id', '')}" 
               style="background: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                Review Violation
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        <p style="color: #6b7280; font-size: 12px;">
            PolicySentinel - AI-Powered Compliance Monitoring
        </p>
    </div>
</body>
</html>
        """
        
        return self.send_email(to_emails, subject, body, html_body)
    
    def send_review_notification(
        self,
        to_emails: List[str],
        review_data: dict
    ) -> bool:
        """
        Send review notification email
        
        Args:
            to_emails: List of recipient emails
            review_data: Review information
            
        Returns:
            True if sent successfully
        """
        action = review_data.get('action', 'reviewed')
        subject = f"✓ Violation {action.title()}"
        
        body = f"""
PolicySentinel Notification

A violation has been {action}.

Violation ID: {review_data.get('violation_id', 'N/A')}
Reviewer: {review_data.get('reviewer_name', 'N/A')}
Action: {action.title()}
Reason: {review_data.get('reason', 'No reason provided')}

View details in the PolicySentinel dashboard.

---
PolicySentinel - AI-Powered Compliance Monitoring
        """
        
        return self.send_email(to_emails, subject, body)
