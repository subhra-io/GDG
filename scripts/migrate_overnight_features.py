"""Database migration for overnight demo features.

This script adds:
1. Risk scoring fields to violations table
2. reasoning_traces table
3. remediation_progress table
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from src.core.database import db_manager
from src.core.logging import get_logger

logger = get_logger(__name__)


def migrate_database():
    """Run database migrations for overnight features."""
    
    logger.info("Starting database migration for overnight features")
    
    # Initialize database connection
    db_manager.initialize_postgres()
    
    session = db_manager.get_postgres_session()
    
    try:
        # Add risk scoring columns to violations table
        logger.info("Adding risk scoring columns to violations table")
        session.execute(text("""
            ALTER TABLE violations 
            ADD COLUMN IF NOT EXISTS risk_score INTEGER,
            ADD COLUMN IF NOT EXISTS risk_level VARCHAR(20),
            ADD COLUMN IF NOT EXISTS risk_factors JSONB;
        """))
        
        # Create reasoning_traces table
        logger.info("Creating reasoning_traces table")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS reasoning_traces (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                violation_id UUID NOT NULL UNIQUE REFERENCES violations(id) ON DELETE CASCADE,
                steps JSONB NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """))
        
        # Create remediation_progress table
        logger.info("Creating remediation_progress table")
        session.execute(text("""
            CREATE TABLE IF NOT EXISTS remediation_progress (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                violation_id UUID NOT NULL REFERENCES violations(id) ON DELETE CASCADE,
                step_index INTEGER NOT NULL,
                step_description TEXT NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE,
                completed_at TIMESTAMP,
                completed_by VARCHAR(255)
            );
        """))
        
        # Create indexes for performance
        logger.info("Creating indexes")
        session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_violations_risk_score ON violations(risk_score);
            CREATE INDEX IF NOT EXISTS idx_violations_risk_level ON violations(risk_level);
            CREATE INDEX IF NOT EXISTS idx_reasoning_traces_violation_id ON reasoning_traces(violation_id);
            CREATE INDEX IF NOT EXISTS idx_remediation_progress_violation_id ON remediation_progress(violation_id);
        """))
        
        session.commit()
        logger.info("Database migration completed successfully")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Migration failed: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate_database()
