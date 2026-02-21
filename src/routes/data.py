"""Data explorer API endpoints."""

from typing import Optional
from fastapi import APIRouter, Query
from sqlalchemy import func, and_

from src.core.database import db_manager
from src.models import CompanyRecord
from src.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/data", tags=["data"])


@router.get("/statistics")
def get_data_statistics():
    """
    Get statistics about loaded dataset.
    
    Returns:
        Dictionary with dataset statistics
    """
    db = db_manager.get_postgres_session()
    try:
        # Total records
        total = db.query(CompanyRecord).count()
        
        if total == 0:
            return {
                "total_records": 0,
                "message": "No data loaded. Use scripts/create_test_scenarios.py or scripts/load_ibm_dataset.py"
            }
        
        # Amount statistics
        amount_stats = db.query(
            func.min(CompanyRecord.amount).label("min_amount"),
            func.max(CompanyRecord.amount).label("max_amount"),
            func.avg(CompanyRecord.amount).label("avg_amount")
        ).first()
        
        # Transaction type distribution
        type_distribution = db.query(
            CompanyRecord.transaction_type,
            func.count(CompanyRecord.id).label("count")
        ).group_by(CompanyRecord.transaction_type).all()
        
        # Laundering statistics (if available)
        laundering_count = db.query(CompanyRecord).filter(
            CompanyRecord.data["is_laundering"].astext == "true"
        ).count()
        
        normal_count = total - laundering_count
        
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
        
    except Exception as e:
        logger.error("Failed to get data statistics", error=str(e))
        return {
            "total_records": 0,
            "error": str(e)
        }
    finally:
        db.close()


@router.get("/records")
def get_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    transaction_type: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    is_laundering: Optional[bool] = None
):
    """
    Get paginated list of records with optional filters.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        transaction_type: Filter by transaction type
        min_amount: Minimum transaction amount
        max_amount: Maximum transaction amount
        is_laundering: Filter by laundering status
        
    Returns:
        Dictionary with records and total count
    """
    db = db_manager.get_postgres_session()
    try:
        # Build query
        query = db.query(CompanyRecord)
        
        # Apply filters
        filters = []
        
        if transaction_type:
            filters.append(CompanyRecord.transaction_type == transaction_type)
        
        if min_amount is not None:
            filters.append(CompanyRecord.amount >= min_amount)
        
        if max_amount is not None:
            filters.append(CompanyRecord.amount <= max_amount)
        
        if is_laundering is not None:
            if is_laundering:
                filters.append(CompanyRecord.data["is_laundering"].astext == "true")
            else:
                filters.append(
                    (CompanyRecord.data["is_laundering"].astext == "false") |
                    (CompanyRecord.data["is_laundering"].astext == None)
                )
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Get total count
        total = query.count()
        
        # Get paginated records
        records = query.order_by(CompanyRecord.timestamp.desc()).offset(skip).limit(limit).all()
        
        # Convert to dict
        records_data = []
        for record in records:
            records_data.append({
                "id": str(record.id),
                "transaction_id": record.transaction_id,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                "from_account": record.from_account,
                "to_account": record.to_account,
                "amount": float(record.amount) if record.amount else 0,
                "transaction_type": record.transaction_type,
                "record_type": record.record_type,
                "data": record.data,
                "created_at": record.created_at.isoformat() if record.created_at else None,
            })
        
        return {
            "records": records_data,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error("Failed to get records", error=str(e))
        return {
            "records": [],
            "total": 0,
            "error": str(e)
        }
    finally:
        db.close()


@router.get("/records/{record_id}")
def get_record_detail(record_id: str):
    """
    Get detailed information about a specific record.
    
    Args:
        record_id: Record ID
        
    Returns:
        Record details
    """
    db = db_manager.get_postgres_session()
    try:
        record = db.query(CompanyRecord).filter(CompanyRecord.id == record_id).first()
        
        if not record:
            return {"error": "Record not found"}
        
        return {
            "id": str(record.id),
            "transaction_id": record.transaction_id,
            "timestamp": record.timestamp.isoformat() if record.timestamp else None,
            "from_account": record.from_account,
            "to_account": record.to_account,
            "amount": float(record.amount) if record.amount else 0,
            "transaction_type": record.transaction_type,
            "record_type": record.record_type,
            "data": record.data,
            "created_at": record.created_at.isoformat() if record.created_at else None,
            "updated_at": record.updated_at.isoformat() if record.updated_at else None,
        }
        
    except Exception as e:
        logger.error("Failed to get record detail", error=str(e), record_id=record_id)
        return {"error": str(e)}
    finally:
        db.close()
