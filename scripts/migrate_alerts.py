"""Database migration for alerts and notifications"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from src.config.settings import settings
from src.models.alert_rule import AlertRule
from src.models.notification import Notification
from src.models.user import User
from src.core.database import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Run migration"""
    try:
        # Create engine
        engine = create_engine(settings.postgres_url)
        
        # Create tables
        logger.info("Creating alert_rules and notifications tables...")
        Base.metadata.create_all(bind=engine, tables=[
            AlertRule.__table__,
            Notification.__table__
        ])
        
        logger.info("✅ Tables created successfully")
        
        # Create sample alert rules
        logger.info("Creating sample alert rules...")
        create_sample_rules(engine)
        
        logger.info("✅ Migration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


def create_sample_rules(engine):
    """Create sample alert rules"""
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get first admin user
        admin = session.query(User).filter(User.role == 'admin').first()
        admin_id = str(admin.id) if admin else None
        
        # Rule 1: Critical Violations
        rule1 = AlertRule(
            name="Critical Violations",
            description="Alert on all critical severity violations",
            trigger_condition={
                "severity": "critical"
            },
            notification_channels=["email", "slack", "in_app"],
            recipients={
                "emails": ["admin@policysentinel.com"],
                "slack_channels": ["#compliance-alerts"],
                "user_ids": [admin_id] if admin_id else []
            },
            is_active=True,
            created_by=admin_id
        )
        
        # Rule 2: High Risk Predictions
        rule2 = AlertRule(
            name="High Risk Predictions",
            description="Alert when risk score exceeds 80",
            trigger_condition={
                "risk_score_min": 80
            },
            notification_channels=["email", "in_app"],
            recipients={
                "emails": ["compliance-team@policysentinel.com"],
                "user_ids": [admin_id] if admin_id else []
            },
            is_active=True,
            created_by=admin_id
        )
        
        # Rule 3: High Severity Violations
        rule3 = AlertRule(
            name="High Severity Violations",
            description="Alert on high severity violations",
            trigger_condition={
                "severity": "high"
            },
            notification_channels=["in_app"],
            recipients={
                "user_ids": [admin_id] if admin_id else []
            },
            is_active=True,
            created_by=admin_id
        )
        
        session.add_all([rule1, rule2, rule3])
        session.commit()
        
        logger.info("✅ Created 3 sample alert rules")
        
        # Display created rules
        rules = session.query(AlertRule).all()
        logger.info("\nCreated Alert Rules:")
        for rule in rules:
            logger.info(f"  - {rule.name} (Active: {rule.is_active})")
            logger.info(f"    Channels: {', '.join(rule.notification_channels)}")
            logger.info(f"    Condition: {rule.trigger_condition}")
        
    except Exception as e:
        logger.error(f"Error creating sample rules: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
