"""IBM AML dataset loader for realistic compliance testing.

Dataset: IBM Transactions for Anti-Money Laundering (AML)
Source: https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml
License: CDLA-Sharing-1.0

This synthetic dataset contains financial transaction data with explicit laundering tags,
providing ground truth for compliance agent testing.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from src.models import CompanyRecord
from src.core.logging import get_logger

logger = get_logger(__name__)


class IBMAMLLoader:
    """Load IBM AML dataset into the database."""
    
    # IBM AML dataset schema mapping
    FIELD_MAPPING = {
        "Timestamp": "timestamp",
        "From Bank": "from_bank",
        "From Account": "from_account",
        "To Bank": "to_bank",
        "To Account": "to_account",
        "Amount Received": "amount",
        "Receiving Currency": "currency",
        "Amount Paid": "amount_paid",
        "Payment Currency": "payment_currency",
        "Payment Format": "payment_format",
        "Is Laundering": "is_laundering",
    }
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize the IBM AML loader.
        
        Args:
            dataset_path: Path to the IBM AML CSV file. If None, looks in common locations.
        """
        self.dataset_path = self._find_dataset(dataset_path)
    
    def _find_dataset(self, provided_path: Optional[str]) -> Optional[Path]:
        """
        Find the IBM AML dataset file.
        
        Args:
            provided_path: User-provided path
            
        Returns:
            Path to dataset file or None if not found
        """
        if provided_path:
            path = Path(provided_path)
            if path.exists():
                return path
            logger.warning("Provided dataset path does not exist", path=provided_path)
        
        # Check common locations
        common_paths = [
            Path("data/ibm_aml.csv"),
            Path("data/HI-Small_Trans.csv"),
            Path("../data/ibm_aml.csv"),
            Path("ibm_aml.csv"),
        ]
        
        for path in common_paths:
            if path.exists():
                logger.info("Found IBM AML dataset", path=str(path))
                return path
        
        logger.warning("IBM AML dataset not found in common locations")
        return None
    
    def load_data(
        self,
        db: Session,
        max_records: Optional[int] = None,
        include_laundering: bool = True,
        include_normal: bool = True
    ) -> int:
        """
        Load IBM AML dataset into the database.
        
        Args:
            db: Database session
            max_records: Maximum number of records to load (None = all)
            include_laundering: Include transactions marked as laundering
            include_normal: Include normal (non-laundering) transactions
            
        Returns:
            Number of records loaded
            
        Raises:
            FileNotFoundError: If dataset file not found
            ValueError: If CSV format is invalid
        """
        if not self.dataset_path:
            raise FileNotFoundError(
                "IBM AML dataset not found. Please download from: "
                "https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml"
            )
        
        logger.info(
            "Loading IBM AML dataset",
            path=str(self.dataset_path),
            max_records=max_records
        )
        
        records_loaded = 0
        records_skipped = 0
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Check if we've reached the limit
                    if max_records and records_loaded >= max_records:
                        break
                    
                    # Filter by laundering status
                    is_laundering = row.get("Is Laundering", "0") == "1"
                    if is_laundering and not include_laundering:
                        records_skipped += 1
                        continue
                    if not is_laundering and not include_normal:
                        records_skipped += 1
                        continue
                    
                    # Transform row to CompanyRecord
                    record = self._transform_row(row)
                    if record:
                        db.add(record)
                        records_loaded += 1
                        
                        # Commit in batches for performance
                        if records_loaded % 1000 == 0:
                            db.commit()
                            logger.info("Progress", records_loaded=records_loaded)
            
            # Final commit
            db.commit()
            
            logger.info(
                "IBM AML dataset loaded successfully",
                records_loaded=records_loaded,
                records_skipped=records_skipped
            )
            
            return records_loaded
            
        except Exception as e:
            db.rollback()
            logger.error("Failed to load IBM AML dataset", error=str(e))
            raise
    
    def _transform_row(self, row: Dict[str, str]) -> Optional[CompanyRecord]:
        """
        Transform a CSV row into a CompanyRecord.
        
        Args:
            row: CSV row as dictionary
            
        Returns:
            CompanyRecord or None if transformation fails
        """
        try:
            # Parse timestamp
            timestamp_str = row.get("Timestamp", "")
            try:
                # Try multiple timestamp formats
                for fmt in ["%Y/%m/%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
                    try:
                        timestamp = datetime.strptime(timestamp_str, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    timestamp = datetime.utcnow()
            except Exception:
                timestamp = datetime.utcnow()
            
            # Parse amount
            amount_str = row.get("Amount Received", "0")
            try:
                amount = float(amount_str.replace(",", ""))
            except (ValueError, AttributeError):
                amount = 0.0
            
            # Parse amount paid
            amount_paid_str = row.get("Amount Paid", "0")
            try:
                amount_paid = float(amount_paid_str.replace(",", ""))
            except (ValueError, AttributeError):
                amount_paid = 0.0
            
            # Determine transaction type based on payment format
            payment_format = row.get("Payment Format", "TRANSFER")
            transaction_type = self._map_payment_format(payment_format)
            
            # Create unique transaction ID
            from_account = row.get("From Account", "UNKNOWN")
            to_account = row.get("To Account", "UNKNOWN")
            transaction_id = f"IBM_{from_account}_{to_account}_{timestamp.strftime('%Y%m%d%H%M%S')}"
            
            # Build data dictionary with all fields
            data = {
                "from_bank": row.get("From Bank", ""),
                "to_bank": row.get("To Bank", ""),
                "currency": row.get("Receiving Currency", "USD"),
                "amount_paid": amount_paid,
                "payment_currency": row.get("Payment Currency", "USD"),
                "payment_format": payment_format,
                "is_laundering": row.get("Is Laundering", "0") == "1",
                "source": "IBM_AML_Dataset",
            }
            
            record = CompanyRecord(
                transaction_id=transaction_id,
                timestamp=timestamp,
                from_account=from_account,
                to_account=to_account,
                amount=amount,
                transaction_type=transaction_type,
                record_type="transaction",
                data=data
            )
            
            return record
            
        except Exception as e:
            logger.warning("Failed to transform row", error=str(e), row=row)
            return None
    
    def _map_payment_format(self, payment_format: str) -> str:
        """
        Map IBM payment format to standard transaction type.
        
        Args:
            payment_format: Payment format from IBM dataset
            
        Returns:
            Standard transaction type
        """
        format_mapping = {
            "Cheque": "PAYMENT",
            "ACH": "TRANSFER",
            "Cash": "CASH_OUT",
            "Credit Card": "PAYMENT",
            "Debit": "DEBIT",
            "Bitcoin": "TRANSFER",
            "Wire": "TRANSFER",
        }
        
        return format_mapping.get(payment_format, "TRANSFER")
    
    def get_statistics(self, db: Session) -> Dict[str, Any]:
        """
        Get statistics about loaded IBM AML data.
        
        Args:
            db: Database session
            
        Returns:
            Dictionary with statistics
        """
        from sqlalchemy import func
        
        # Count total records from IBM dataset
        total = db.query(CompanyRecord).filter(
            CompanyRecord.data["source"].astext == "IBM_AML_Dataset"
        ).count()
        
        if total == 0:
            return {
                "total_records": 0,
                "message": "No IBM AML data loaded"
            }
        
        # Count laundering vs normal
        laundering_count = db.query(CompanyRecord).filter(
            CompanyRecord.data["source"].astext == "IBM_AML_Dataset",
            CompanyRecord.data["is_laundering"].astext == "true"
        ).count()
        
        normal_count = total - laundering_count
        
        # Get amount statistics
        amount_stats = db.query(
            func.min(CompanyRecord.amount).label("min_amount"),
            func.max(CompanyRecord.amount).label("max_amount"),
            func.avg(CompanyRecord.amount).label("avg_amount")
        ).filter(
            CompanyRecord.data["source"].astext == "IBM_AML_Dataset"
        ).first()
        
        # Get transaction type distribution
        type_distribution = db.query(
            CompanyRecord.transaction_type,
            func.count(CompanyRecord.id).label("count")
        ).filter(
            CompanyRecord.data["source"].astext == "IBM_AML_Dataset"
        ).group_by(CompanyRecord.transaction_type).all()
        
        return {
            "total_records": total,
            "laundering_transactions": laundering_count,
            "normal_transactions": normal_count,
            "laundering_percentage": round(laundering_count / total * 100, 2) if total > 0 else 0,
            "amount_min": float(amount_stats.min_amount) if amount_stats.min_amount else 0,
            "amount_max": float(amount_stats.max_amount) if amount_stats.max_amount else 0,
            "amount_avg": round(float(amount_stats.avg_amount), 2) if amount_stats.avg_amount else 0,
            "transaction_types": {t: c for t, c in type_distribution}
        }
