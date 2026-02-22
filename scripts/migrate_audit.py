"""Database migration for audit trail"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from src.config.settings import settings
from src.models.audit_log import AuditLog
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
        logger.info("Creating audit_logs table...")
        Base.metadata.create_all(bind=engine, tables=[
            AuditLog.__table__
        ])
        
        logger.info("✅ Table created successfully")
        
        # Create indexes
        logger.info("Creating indexes...")
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp 
                ON audit_logs(timestamp);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id 
                ON audit_logs(user_id);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type 
                ON audit_logs(event_type);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_type 
                ON audit_logs(resource_type);
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_audit_logs_resource_id 
                ON audit_logs(resource_id);
            """))
            conn.commit()
        
        logger.info("✅ Indexes created successfully")
        
        # Create sample audit logs
        logger.info("Creating sample audit logs...")
        create_sample_logs(engine)
        
        logger.info("✅ Migration completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


def create_sample_logs(engine):
    """Create sample audit logs"""
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime, timedelta
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Sample log 1: Policy upload
        log1 = AuditLog(
            timestamp=datetime.utcnow() - timedelta(hours=2),
            event_type="user_action",
            action="create",
            resource_type="policy",
            resource_id="f7e759f0-240c-4233-877c-2686d39d9f36",
            user_email="admin@policysentinel.com",
            ip_address="127.0.0.1",
            request_method="POST",
            request_path="/api/v1/policies",
            response_status=201,
            duration_ms=1250
        )
        
        # Sample log 2: AI rule extraction
        log2 = AuditLog(
            timestamp=datetime.utcnow() - timedelta(hours=2, minutes=1),
            event_type="ai_decision",
            action="execute",
            resource_type="rule",
            resource_id="f7e759f0-240c-4233-877c-2686d39d9f36",
            user_email="AI Agent",
            ai_model="gpt-4",
            ai_confidence=0.95,
            duration_ms=3500
        )
        
        # Sample log 3: Violation detection
        log3 = AuditLog(
            timestamp=datetime.utcnow() - timedelta(hours=1),
            event_type="ai_decision",
            action="execute",
            resource_type="violation",
            user_email="AI Agent",
            ai_model="gpt-4",
            ai_confidence=0.92,
            duration_ms=2100
        )
        
        # Sample log 4: Review submission
        log4 = AuditLog(
            timestamp=datetime.utcnow() - timedelta(minutes=30),
            event_type="user_action",
            action="update",
            resource_type="review",
            user_email="john.doe@policysentinel.com",
            ip_address="127.0.0.1",
            request_method="POST",
            request_path="/api/v1/reviews",
            response_status=200,
            duration_ms=450
        )
        
        # Sample log 5: Alert sent
        log5 = AuditLog(
            timestamp=datetime.utcnow() - timedelta(minutes=15),
            event_type="system_event",
            action="execute",
            resource_type="notification",
            user_email="System",
            duration_ms=850
        )
        
        session.add_all([log1, log2, log3, log4, log5])
        session.commit()
        
        logger.info("✅ Created 5 sample audit logs")
        
        # Display created logs
        logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(5).all()
        logger.info("\nSample Audit Logs:")
        for log in logs:
            logger.info(f"  - {log.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | "
                       f"{log.event_type} | {log.action} | {log.resource_type}")
        
    except Exception as e:
        logger.error(f"Error creating sample logs: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()
