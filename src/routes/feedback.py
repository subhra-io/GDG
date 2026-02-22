"""API routes for feedback loop system."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging

from src.core.database import get_db
from src.services.analytics_engine import AnalyticsEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/feedback", tags=["feedback"])


def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """Parse date string to datetime."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except Exception:
        return None


@router.get("/metrics")
async def get_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get overall accuracy metrics.
    
    - **start_date**: Optional start date (ISO format)
    - **end_date**: Optional end date (ISO format)
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        metrics = AnalyticsEngine.get_overall_metrics(db, start, end)
        return metrics
        
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules")
async def get_rule_metrics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get per-rule correction statistics.
    
    - **start_date**: Optional start date (ISO format)
    - **end_date**: Optional end date (ISO format)
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        metrics = AnalyticsEngine.get_rule_metrics(db, start, end)
        return {
            "rules": metrics,
            "count": len(metrics)
        }
        
    except Exception as e:
        logger.error(f"Error getting rule metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_correction_history(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    rule_id: Optional[str] = None,
    reviewer_id: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get correction history with pagination and filters.
    
    - **limit**: Maximum number of results (1-500)
    - **offset**: Pagination offset
    - **rule_id**: Filter by rule ID
    - **reviewer_id**: Filter by reviewer ID
    - **start_date**: Filter by start date (ISO format)
    - **end_date**: Filter by end date (ISO format)
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        result = AnalyticsEngine.get_correction_history(
            db, limit, offset, rule_id, reviewer_id, start, end
        )
        return result
        
    except Exception as e:
        logger.error(f"Error getting correction history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_improvement_suggestions(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get improvement suggestions based on correction patterns.
    
    - **start_date**: Optional start date (ISO format)
    - **end_date**: Optional end date (ISO format)
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        suggestions = AnalyticsEngine.get_improvement_suggestions(db, start, end)
        return {
            "suggestions": suggestions,
            "count": len(suggestions)
        }
        
    except Exception as e:
        logger.error(f"Error getting suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trends")
async def get_trend_data(
    start_date: str,
    end_date: str,
    granularity: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db)
):
    """
    Get time-series data for correction trends.
    
    - **start_date**: Start date (ISO format, required)
    - **end_date**: End date (ISO format, required)
    - **granularity**: Time granularity (day, week, month)
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        if not start or not end:
            raise HTTPException(status_code=400, detail="Invalid date format")
        
        trends = AnalyticsEngine.get_trend_data(db, start, end, granularity)
        return {
            "trends": trends,
            "count": len(trends)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting trend data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reviewers")
async def get_reviewer_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get per-reviewer statistics.
    
    - **start_date**: Optional start date (ISO format)
    - **end_date**: Optional end date (ISO format)
    """
    try:
        start = parse_date(start_date)
        end = parse_date(end_date)
        
        stats = AnalyticsEngine.get_reviewer_statistics(db, start, end)
        return {
            "reviewers": stats,
            "count": len(stats)
        }
        
    except Exception as e:
        logger.error(f"Error getting reviewer statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
