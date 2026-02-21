"""Violation management routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import db_manager
from src.core.logging import get_logger
from src.models import Violation, ComplianceRule, CompanyRecord, ReasoningTrace
from src.schemas import ViolationResponse, ViolationDetailResponse
from src.services import ViolationDetector, RuleExtractor, RiskScoringEngine, ReasoningTraceGenerator

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/violations", tags=["violations"])


def get_db():
    """Get database session."""
    session = db_manager.get_postgres_session()
    try:
        yield session
    finally:
        session.close()


@router.post("/scan")
async def scan_for_violations(db: Session = Depends(get_db)):
    """
    Scan all company records against active rules to detect violations.
    
    Args:
        db: Database session
        
    Returns:
        Scan results
    """
    try:
        # Get active rules
        rules = db.query(ComplianceRule).filter(
            ComplianceRule.is_active == True
        ).all()
        
        if not rules:
            return {
                "status": "success",
                "message": "No active rules to scan",
                "violations_detected": 0
            }
        
        # Get company records
        records = db.query(CompanyRecord).all()
        
        if not records:
            return {
                "status": "success",
                "message": "No records to scan",
                "violations_detected": 0
            }
        
        # Initialize services
        violation_detector = ViolationDetector()
        rule_extractor = RuleExtractor()
        risk_engine = RiskScoringEngine()
        reasoning_generator = ReasoningTraceGenerator()
        
        violations_created = 0
        
        # Scan each record against each rule
        for record in records:
            record_data = {
                "id": str(record.id),
                "transaction_id": record.transaction_id,
                "amount": record.amount,
                "transaction_type": record.transaction_type,
                "from_account": record.from_account,
                "to_account": record.to_account,
                "timestamp": record.timestamp.isoformat() if record.timestamp else None,
                **record.data
            }
            
            for rule in rules:
                rule_dict = {
                    "id": str(rule.id),
                    "description": rule.description,
                    "validation_logic": rule.validation_logic,
                    "severity": rule.severity.value
                }
                
                # Check if violation exists
                violation_result = violation_detector.evaluate_record(
                    record_data,
                    rule_dict
                )
                
                if violation_result:
                    # Check if violation already exists
                    existing = db.query(Violation).filter(
                        Violation.rule_id == rule.id,
                        Violation.record_identifier == str(record.id)
                    ).first()
                    
                    if not existing:
                        # Generate justification
                        justification = rule_extractor.generate_justification(
                            rule.description,
                            record_data,
                            violation_result["violation_details"]
                        )
                        
                        # Generate remediation steps
                        remediation = rule_extractor.generate_remediation_steps(
                            rule.description,
                            justification,
                            record_data
                        )
                        
                        # Create violation
                        violation = Violation(
                            rule_id=rule.id,
                            record_identifier=str(record.id),
                            table_name="company_records",
                            justification=justification,
                            record_snapshot=record_data,
                            severity=rule.severity.value,
                            remediation_steps=remediation
                        )
                        
                        db.add(violation)
                        db.flush()  # Get violation ID
                        
                        # Calculate risk score
                        risk_data = risk_engine.calculate_risk_score(
                            violation,
                            record_data,
                            db
                        )
                        
                        violation.risk_score = risk_data["score"]
                        violation.risk_level = risk_data["level"]
                        violation.risk_factors = risk_data["factors"]
                        
                        # Generate reasoning trace
                        try:
                            reasoning_steps = reasoning_generator.generate_trace(
                                rule.description,
                                rule.severity.value,
                                record_data,
                                violation_result["violation_details"]
                            )
                            
                            reasoning_trace = ReasoningTrace(
                                violation_id=violation.id,
                                steps=reasoning_steps
                            )
                            db.add(reasoning_trace)
                        except Exception as e:
                            logger.warning(f"Failed to generate reasoning trace: {e}")
                        
                        violations_created += 1
        
        db.commit()
        
        logger.info(
            "Violation scan completed",
            rules_scanned=len(rules),
            records_scanned=len(records),
            violations_created=violations_created
        )
        
        return {
            "status": "success",
            "message": f"Scan completed successfully",
            "rules_scanned": len(rules),
            "records_scanned": len(records),
            "violations_detected": violations_created
        }
        
    except Exception as e:
        logger.error("Violation scan failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("", response_model=List[ViolationResponse])
async def list_violations(
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    risk_level: Optional[str] = Query(None),
    sort_by: Optional[str] = Query("detected_at", regex="^(detected_at|risk_score)$"),
    order: Optional[str] = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    List violations with optional filters and sorting.
    
    Args:
        status: Filter by status
        severity: Filter by severity
        risk_level: Filter by risk level (Low/Medium/High/Critical)
        sort_by: Sort field (detected_at or risk_score)
        order: Sort order (asc or desc)
        limit: Maximum number of results
        db: Database session
        
    Returns:
        List of violations
    """
    query = db.query(Violation)
    
    if status:
        query = query.filter(Violation.status == status)
    
    if severity:
        query = query.filter(Violation.severity == severity)
    
    if risk_level:
        query = query.filter(Violation.risk_level == risk_level)
    
    # Apply sorting
    if sort_by == "risk_score":
        if order == "desc":
            query = query.order_by(Violation.risk_score.desc().nullslast())
        else:
            query = query.order_by(Violation.risk_score.asc().nullsfirst())
    else:  # detected_at
        if order == "desc":
            query = query.order_by(Violation.detected_at.desc())
        else:
            query = query.order_by(Violation.detected_at.asc())
    
    violations = query.limit(limit).all()
    
    return [ViolationResponse.model_validate(v) for v in violations]


@router.get("/{violation_id}", response_model=ViolationDetailResponse)
async def get_violation(violation_id: str, db: Session = Depends(get_db)):
    """
    Get detailed information about a specific violation.
    
    Args:
        violation_id: Violation ID
        db: Database session
        
    Returns:
        Violation details
    """
    violation = db.query(Violation).filter(
        Violation.id == violation_id
    ).first()
    
    if not violation:
        raise HTTPException(status_code=404, detail="Violation not found")
    
    return ViolationDetailResponse.model_validate(violation)


@router.get("/stats/summary")
async def get_violation_stats(db: Session = Depends(get_db)):
    """
    Get violation statistics summary.
    
    Args:
        db: Database session
        
    Returns:
        Statistics summary
    """
    total = db.query(Violation).count()
    
    by_severity = {}
    for severity in ["critical", "high", "medium", "low"]:
        count = db.query(Violation).filter(
            Violation.severity == severity
        ).count()
        by_severity[severity] = count
    
    by_status = {}
    for status in ["pending_review", "confirmed", "dismissed", "resolved"]:
        count = db.query(Violation).filter(
            Violation.status == status
        ).count()
        by_status[status] = count
    
    return {
        "total_violations": total,
        "by_severity": by_severity,
        "by_status": by_status
    }


@router.get("/{violation_id}/reasoning-trace")
async def get_reasoning_trace(violation_id: str, db: Session = Depends(get_db)):
    """
    Get reasoning trace for a violation.
    
    Args:
        violation_id: Violation ID
        db: Database session
        
    Returns:
        Reasoning trace with steps
    """
    trace = db.query(ReasoningTrace).filter(
        ReasoningTrace.violation_id == violation_id
    ).first()
    
    if not trace:
        raise HTTPException(status_code=404, detail="Reasoning trace not found")
    
    return {
        "id": str(trace.id),
        "violation_id": str(trace.violation_id),
        "steps": trace.steps,
        "created_at": trace.created_at.isoformat()
    }


@router.get("/{violation_id}/reasoning-trace/export")
async def export_reasoning_trace(violation_id: str, db: Session = Depends(get_db)):
    """
    Export reasoning trace as plain text.
    
    Args:
        violation_id: Violation ID
        db: Database session
        
    Returns:
        Plain text reasoning trace
    """
    from fastapi.responses import PlainTextResponse
    
    trace = db.query(ReasoningTrace).filter(
        ReasoningTrace.violation_id == violation_id
    ).first()
    
    if not trace:
        raise HTTPException(status_code=404, detail="Reasoning trace not found")
    
    reasoning_generator = ReasoningTraceGenerator()
    text_content = reasoning_generator.format_trace_for_export(trace.steps)
    
    return PlainTextResponse(
        content=text_content,
        headers={
            "Content-Disposition": f"attachment; filename=reasoning_trace_{violation_id}.txt"
        }
    )
