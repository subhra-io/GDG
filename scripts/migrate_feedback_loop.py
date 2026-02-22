"""Database migration for feedback loop system."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from src.config.settings import settings
from src.core.database import Base
from src.models.correction import Correction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Create corrections table and indexes."""
    try:
        engine = create_engine(settings.postgres_url)
        
        logger.info("Creating corrections table...")
        
        # Create table
        Base.metadata.create_all(engine, tables=[Correction.__table__])
        
        # Create indexes
        with engine.connect() as conn:
            logger.info("Creating indexes...")
            
            # Index on violation_id
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_corrections_violation_id 
                ON corrections(violation_id)
            """))
            
            # Index on rule_id
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_corrections_rule_id 
                ON corrections(rule_id)
            """))
            
            # Index on corrected_by
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_corrections_corrected_by 
                ON corrections(corrected_by)
            """))
            
            # Index on created_at
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_corrections_created_at 
                ON corrections(created_at)
            """))
            
            # Composite index on (rule_id, corrected_decision)
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_corrections_rule_decision 
                ON corrections(rule_id, corrected_decision)
            """))
            
            conn.commit()
        
        logger.info("✅ Corrections table and indexes created successfully!")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {str(e)}")
        raise


if __name__ == "__main__":
    migrate()
