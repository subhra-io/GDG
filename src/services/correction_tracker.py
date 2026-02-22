"""Service for tracking corrections to AI decisions."""

import logging
from typing import Optional
from sqlalchemy.orm import Session

from src.models.correction import Correction, CorrectedDecision
from src.models.violation import Violation, ReviewAction
from src.models.rule import ComplianceRule

logger = logging.getLogger(__name__)


class CorrectionTracker:
    """Service for tracking corrections to AI decisions."""
    
    @staticmethod
    def track_correction(
        db: Session,
        violation_id: str,
        review_action: ReviewAction,
        reviewer_user_id: str,
        reason: Optional[str] = None
    ) -> Optional[Correction]:
        """
        Create a correction record from a review action.
        
        Args:
            db: Database session
            violation_id: ID of the violation being reviewed
            review_action: The review action taken (confirm/dismiss/request_more_info)
            reviewer_user_id: ID of the user who performed the review
            reason: Optional reason provided by reviewer
            
        Returns:
            Created Correction object or None if failed
        """
        try:
            # Fetch violation with rule information
            violation = db.query(Violation).filter(Violation.id == violation_id).first()
            if not violation:
                logger.warning(f"Violation {violation_id} not found for correction tracking")
                return None
            
            # Get rule information
            rule = db.query(ComplianceRule).filter(ComplianceRule.id == violation.rule_id).first()
            if not rule:
                logger.warning(f"Rule {violation.rule_id} not found for correction tracking")
                return None
            
            # Map review action to corrected decision
            corrected_decision = CorrectionTracker._map_action_to_decision(review_action)
            
            # Extract ai_confidence if available (from risk_score)
            ai_confidence = None
            if violation.risk_score is not None:
                ai_confidence = violation.risk_score / 100.0  # Convert 0-100 to 0.0-1.0
            
            # Create correction record
            correction = Correction(
                violation_id=violation_id,
                rule_id=violation.rule_id,
                rule_name=rule.description[:255] if rule.description else "Unknown Rule",  # Use description as name
                original_decision="violation_detected",
                corrected_decision=corrected_decision,
                corrected_by=reviewer_user_id,
                correction_reason=reason,
                ai_confidence=ai_confidence,
                severity=violation.severity
            )
            
            db.add(correction)
            db.commit()
            db.refresh(correction)
            
            logger.info(f"Correction tracked: {violation_id} -> {corrected_decision.value}")
            return correction
            
        except Exception as e:
            logger.error(f"Failed to track correction for {violation_id}: {str(e)}")
            db.rollback()
            return None
    
    @staticmethod
    def _map_action_to_decision(action: ReviewAction) -> CorrectedDecision:
        """
        Map review action to corrected decision type.
        
        confirm -> true_positive
        dismiss -> false_positive
        request_more_info -> needs_review
        """
        mapping = {
            ReviewAction.CONFIRM: CorrectedDecision.TRUE_POSITIVE,
            ReviewAction.DISMISS: CorrectedDecision.FALSE_POSITIVE,
            ReviewAction.REQUEST_MORE_INFO: CorrectedDecision.NEEDS_REVIEW
        }
        return mapping.get(action, CorrectedDecision.NEEDS_REVIEW)
