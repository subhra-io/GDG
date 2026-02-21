"""Dashboard and analytics routes."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Optional

from src.core.database import db_manager
from src.models import Violation, ComplianceRule, CompanyRecord
from src.services import ViolationDetector, RiskScoringEngine

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


def get_db():
    """Get database session."""
    session = db_manager.get_postgres_session()
    try:
        yield session
    finally:
        session.close()


@router.get("/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """
    Get key dashboard metrics.
    
    Args:
        db: Database session
        
    Returns:
        Dashboard metrics
    """
    # Total violations (all)
    total_violations = db.query(Violation).count()
    
    # Active violations (not resolved)
    active_violations = db.query(Violation).filter(
        Violation.status != "resolved"
    ).count()
    
    # Total rules
    total_rules = db.query(ComplianceRule).filter(
        ComplianceRule.is_active == True
    ).count()
    
    # Total records
    total_records = db.query(CompanyRecord).count()
    
    # Calculate compliance score based on ACTIVE (non-resolved) violations only
    # Use a more reasonable penalty scale for better scores
    if active_violations == 0:
        compliance_score = 100
    else:
        # Get severity counts for active violations only
        severity_counts = {
            "critical": db.query(Violation).filter(
                Violation.severity == "critical",
                Violation.status != "resolved"
            ).count(),
            "high": db.query(Violation).filter(
                Violation.severity == "high",
                Violation.status != "resolved"
            ).count(),
            "medium": db.query(Violation).filter(
                Violation.severity == "medium",
                Violation.status != "resolved"
            ).count(),
            "low": db.query(Violation).filter(
                Violation.severity == "low",
                Violation.status != "resolved"
            ).count()
        }
        
        # Calculate penalty with adjusted scale (less harsh)
        # Critical: 5 points each, High: 2 points, Medium: 1 point, Low: 0.5 points
        penalty = (
            severity_counts["critical"] * 5 +
            severity_counts["high"] * 2 +
            severity_counts["medium"] * 1 +
            severity_counts["low"] * 0.5
        )
        
        # Calculate score (minimum 0, maximum 100)
        # Use a logarithmic scale for better distribution
        if penalty <= 50:
            compliance_score = int(100 - penalty)
        else:
            # For high penalties, use logarithmic decay
            compliance_score = int(50 * (1 - (penalty - 50) / (penalty + 50)))
        
        compliance_score = max(0, min(100, compliance_score))
    
    # Violations by severity (all violations, not just active)
    violations_by_severity = {
        "critical": db.query(Violation).filter(Violation.severity == "critical").count(),
        "high": db.query(Violation).filter(Violation.severity == "high").count(),
        "medium": db.query(Violation).filter(Violation.severity == "medium").count(),
        "low": db.query(Violation).filter(Violation.severity == "low").count()
    }
    
    return {
        "total_violations": total_violations,
        "active_violations": active_violations,
        "total_rules": total_rules,
        "total_records": total_records,
        "compliance_score": compliance_score,
        "violations_by_severity": violations_by_severity
    }


@router.get("/risk-score")
async def get_risk_score(db: Session = Depends(get_db)):
    """
    Get current compliance risk score.
    
    Args:
        db: Database session
        
    Returns:
        Risk score and breakdown
    """
    # Count by severity efficiently (only non-resolved)
    severity_breakdown = {
        "critical": db.query(Violation).filter(
            Violation.severity == "critical",
            Violation.status != "resolved"
        ).count(),
        "high": db.query(Violation).filter(
            Violation.severity == "high",
            Violation.status != "resolved"
        ).count(),
        "medium": db.query(Violation).filter(
            Violation.severity == "medium",
            Violation.status != "resolved"
        ).count(),
        "low": db.query(Violation).filter(
            Violation.severity == "low",
            Violation.status != "resolved"
        ).count()
    }
    
    total_violations = sum(severity_breakdown.values())
    
    # Calculate compliance score with adjusted scale
    if total_violations == 0:
        score = 100
    else:
        # Calculate penalty with adjusted scale
        penalty = (
            severity_breakdown["critical"] * 5 +
            severity_breakdown["high"] * 2 +
            severity_breakdown["medium"] * 1 +
            severity_breakdown["low"] * 0.5
        )
        
        # Calculate score with logarithmic scale for better distribution
        if penalty <= 50:
            score = int(100 - penalty)
        else:
            score = int(50 * (1 - (penalty - 50) / (penalty + 50)))
        
        score = max(0, min(100, score))
    
    return {
        "score": score,
        "total_violations": total_violations,
        "severity_breakdown": severity_breakdown,
        "status": "healthy" if score >= 80 else "at_risk" if score >= 60 else "critical"
    }


@router.get("/trends")
async def get_trends(db: Session = Depends(get_db)):
    """
    Get violation trends over time.
    
    Args:
        db: Database session
        
    Returns:
        Trend data
    """
    # Get violations grouped by date
    result = db.execute(
        text("""
            SELECT 
                DATE(detected_at) as date,
                COUNT(*) as count,
                severity
            FROM violations
            WHERE detected_at >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY DATE(detected_at), severity
            ORDER BY date DESC
        """)
    )
    
    trends = []
    for row in result:
        trends.append({
            "date": str(row[0]),
            "count": row[1],
            "severity": row[2]
        })
    
    return {
        "trends": trends,
        "period": "30_days"
    }


@router.get("/risk-distribution")
async def get_risk_distribution(db: Session = Depends(get_db)):
    """
    Get violation count by risk level.
    
    Args:
        db: Database session
        
    Returns:
        Risk distribution with counts for each level
    """
    # Count violations by risk level
    risk_distribution = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0
    }
    
    for level in ["Low", "Medium", "High", "Critical"]:
        count = db.query(Violation).filter(
            Violation.risk_level == level
        ).count()
        risk_distribution[level.lower()] = count
    
    return {
        "distribution": risk_distribution,
        "total": sum(risk_distribution.values())
    }


@router.get("/risk-trend")
async def get_risk_trend(
    days: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get risk trend over time.
    
    Args:
        days: Number of days to analyze (1-90)
        db: Database session
        
    Returns:
        Daily risk trend data
    """
    risk_engine = RiskScoringEngine()
    trend_data = risk_engine.calculate_risk_trend(db, days)
    
    return {
        "trend": trend_data,
        "period_days": days
    }
