"""Backfill corrections from existing violation reviews."""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from src.core.database import db_manager
from src.models.violation import ViolationReview
from src.services.correction_tracker import CorrectionTracker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def backfill_corrections():
    """Backfill corrections from existing reviews."""
    try:
        # Initialize database
        db_manager.initialize_postgres()
        db: Session = db_manager.get_postgres_session()
        
        # Get all existing reviews
        reviews = db.query(ViolationReview).all()
        
        logger.info(f"Found {len(reviews)} existing reviews to backfill")
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for review in reviews:
            try:
                # Track correction
                correction = CorrectionTracker.track_correction(
                    db=db,
                    violation_id=str(review.violation_id),
                    review_action=review.action,
                    reviewer_user_id=review.reviewer_user_id,
                    reason=review.reason
                )
                
                if correction:
                    success_count += 1
                    if success_count % 10 == 0:
                        logger.info(f"Progress: {success_count} corrections created")
                else:
                    skip_count += 1
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Error backfilling review {review.id}: {str(e)}")
        
        logger.info(f"""
✅ Backfill complete!
   - Created: {success_count} corrections
   - Skipped: {skip_count} reviews
   - Errors: {error_count} reviews
        """)
        
    except Exception as e:
        logger.error(f"❌ Backfill failed: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    backfill_corrections()
