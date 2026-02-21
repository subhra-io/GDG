"""Dashboard and analytics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text

from src.core.database import db_manager
from src.models import Violation, ComplianceRule, CompanyRecord
from src.services import ViolationDetector

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
    # Total violations
    total_violations = db.query(Violation).count()
    
    # Active violations (pending or confirmed)
    active_violations = db.query(Violation).filter(
        Violation.status.in_(["pending_review", "confirmed"])
    ).count()
    
    # Total rules
    total_rules = db.query(ComplianceRule).filter(
        ComplianceRule.is_active == True
    ).count()
    
    # Total records
    total_records = db.query(CompanyRecord).count()
    
    # Calculate risk score
    violations = db.query(Violation).all()
    violation_detector = ViolationDetector()
    violations_data = [
        {"severity": v.severity}
        for v in violations
    ]
    risk_score = violation_detector.calculate_risk_score(violations_data)
    
    # Violations by severity
    violations_by_severity = {}
    for severity in ["critical", "high", "medium", "low"]:
        count = db.query(Violation).filter(
            Violation.severity == severity
        ).count()
        violations_by_severity[severity] = count
    
    return {
        "total_violations": total_violations,
        "active_violations": active_violations,
        "total_rules": total_rules,
        "total_records": total_records,
        "compliance_score": risk_score,
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
    violations = db.query(Violation).all()
    
    violation_detector = ViolationDetector()
    violations_data = [
        {"severity": v.severity}
        for v in violations
    ]
    
    score = violation_detector.calculate_risk_score(violations_data)
    
    # Count by severity
    severity_breakdown = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }
    
    for v in violations:
        if v.severity in severity_breakdown:
            severity_breakdown[v.severity] += 1
    
    return {
        "score": score,
        "total_violations": len(violations),
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
