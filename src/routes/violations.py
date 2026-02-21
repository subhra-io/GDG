"""Violation management routes."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import db_manager
from src.core.logging import get_logger
from src.models import Violation, ComplianceRule, CompanyRecord
from src.schemas import ViolationResponse, ViolationDetailResponse
from src.services import ViolationDetector, RuleExtractor

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
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """
    List violations with optional filters.
    
    Args:
        status: Filter by status
        severity: Filter by severity
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
    
    violations = query.order_by(
        Violation.detected_at.desc()
    ).limit(limit).all()
    
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
