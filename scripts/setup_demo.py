#!/usr/bin/env python3
"""Setup script for demo environment."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import db_manager, Base
from src.core.logging import setup_logging, get_logger
from src.utils.sample_data import load_sample_data

setup_logging()
logger = get_logger(__name__)


def main():
    """Setup demo environment."""
    try:
        logger.info("Setting up demo environment")
        
        # Initialize databases
        logger.info("Initializing database connections")
        db_manager.initialize_postgres()
        db_manager.initialize_mongodb()
        db_manager.initialize_redis()
        
        # Create tables
        logger.info("Creating database tables")
        engine = db_manager._postgres_engine
        Base.metadata.create_all(bind=engine)
        
        # Load sample data
        logger.info("Loading sample data")
        session = db_manager.get_postgres_session()
        try:
            records_created = load_sample_data(session, count=20)
            logger.info("Sample data loaded", records=records_created)
        finally:
            session.close()
        
        logger.info("Demo environment setup complete!")
        logger.info("You can now:")
        logger.info("1. Start the server: python src/main.py")
        logger.info("2. Upload a policy PDF: POST /api/v1/policies/upload")
        logger.info("3. Extract rules: POST /api/v1/policies/{id}/extract-rules")
        logger.info("4. Scan for violations: POST /api/v1/violations/scan")
        logger.info("5. View dashboard: GET /api/v1/dashboard/metrics")
        
    except Exception as e:
        logger.error("Setup failed", error=str(e))
        sys.exit(1)
    finally:
        db_manager.close_all()


if __name__ == "__main__":
    main()
