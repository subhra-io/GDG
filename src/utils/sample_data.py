"""Sample data loader for testing and demo."""

from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session

from src.models import CompanyRecord
from src.core.logging import get_logger

logger = get_logger(__name__)


def load_sample_data(db: Session, count: int = 20) -> int:
    """
    Load sample financial transaction records for testing.
    
    Args:
        db: Database session
        count: Number of records to create
        
    Returns:
        Number of records created
    """
    # Check if data already exists
    existing_count = db.query(CompanyRecord).count()
    if existing_count > 0:
        logger.info("Sample data already exists", count=existing_count)
        return 0
    
    logger.info("Loading sample data", count=count)
    
    transaction_types = ["TRANSFER", "CASH_OUT", "PAYMENT", "DEBIT", "CASH_IN"]
    accounts = [f"ACC{i:04d}" for i in range(1, 21)]
    
    records_created = 0
    base_time = datetime.utcnow() - timedelta(days=30)
    
    for i in range(count):
        # Create varied transactions - some will violate rules
        amount = random.choice([
            random.uniform(100, 5000),  # Normal
            random.uniform(10000, 50000),  # High (potential violation)
            random.uniform(100000, 500000),  # Very high (likely violation)
        ])
        
        transaction_type = random.choice(transaction_types)
        from_account = random.choice(accounts)
        to_account = random.choice([a for a in accounts if a != from_account])
        
        timestamp = base_time + timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        
        record = CompanyRecord(
            transaction_id=f"TXN{i+1:06d}",
            timestamp=timestamp,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            transaction_type=transaction_type,
            record_type="transaction",
            data={
                "currency": "USD",
                "status": "completed",
                "channel": random.choice(["online", "mobile", "branch"]),
                "description": f"Sample transaction {i+1}"
            }
        )
        
        db.add(record)
        records_created += 1
    
    db.commit()
    
    logger.info("Sample data loaded successfully", records_created=records_created)
    return records_created
