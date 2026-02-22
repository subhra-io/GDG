"""Review service for human review workflow."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.models.violation import Violation, ViolationReview, ViolationStatus, ReviewAction
from src.models.user import User
from src.services.correction_tracker import CorrectionTracker

logger = logging.getLogger(__name__)


class ReviewService:
    """Service for managing violation reviews."""
    
    @staticmethod
    def get_review_queue(
        db: Session,
        status: Optional[str] = None,
        assigned_to: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Get list of violations pending review."""
        try:
            # Base query
            query = db.query(Violation)
            
            # Filter by status
            if status:
                query = query.filter(Violation.status == status)
            else:
                # Default to pending review
                query = query.filter(Violation.status == ViolationStatus.PENDING_REVIEW)
            
            # Filter by assigned user
            if assigned_to:
                query = query.filter(Violation.assigned_to == assigned_to)
            
            # Filter by severity
            if severity:
                query = query.filter(Violation.severity == severity)
            
            # Get total count
            total_count = query.count()
            
            # Get paginated results
            violations = query.order_by(
                Violation.detected_at.desc()
            ).limit(limit).offset(offset).all()
            
            # Convert to dict with user info
            results = []
            for violation in violations:
                violation_dict = {
                    "id": str(violation.id),
                    "record_identifier": violation.record_identifier,
                    "severity": violation.severity,
                    "status": violation.status.value,
                    "justification": violation.justification,
                    "detected_at": violation.detected_at.isoformat() if violation.detected_at else None,
                    "risk_score": violation.risk_score,
                    "assigned_to": str(violation.assigned_to) if violation.assigned_to else None,
                    "is_false_positive": violation.is_false_positive == "true"
                }
                
                # Get assigned user info
                if violation.assigned_to:
                    user = db.query(User).filter(User.id == violation.assigned_to).first()
                    if user:
                        violation_dict["assigned_user"] = user.to_dict()
                
                results.append(violation_dict)
            
            return {
                "violations": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting review queue: {str(e)}")
            raise
    
    @staticmethod
    def submit_review(
        db: Session,
        violation_id: str,
        reviewer_user_id: str,
        action: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """Submit a review action for a violation."""
        try:
            # Get violation
            violation = db.query(Violation).filter(Violation.id == violation_id).first()
            if not violation:
                raise ValueError(f"Violation {violation_id} not found")
            
            # Validate action
            try:
                review_action = ReviewAction(action)
            except ValueError:
                raise ValueError(f"Invalid action: {action}")
            
            # Create review record
            review = ViolationReview(
                violation_id=violation_id,
                reviewer_user_id=reviewer_user_id,
                action=review_action,
                reason=reason
            )
            db.add(review)
            
            # Update violation status based on action
            if review_action == ReviewAction.CONFIRM:
                violation.status = ViolationStatus.CONFIRMED
                violation.is_false_positive = "false"
            elif review_action == ReviewAction.DISMISS:
                violation.status = ViolationStatus.DISMISSED
                violation.is_false_positive = "true"
            elif review_action == ReviewAction.REQUEST_MORE_INFO:
                # Keep as pending review
                pass
            
            db.commit()
            db.refresh(review)
            
            # Track correction (graceful failure - don't block review submission)
            try:
                CorrectionTracker.track_correction(
                    db=db,
                    violation_id=violation_id,
                    review_action=review_action,
                    reviewer_user_id=reviewer_user_id,
                    reason=reason
                )
            except Exception as e:
                logger.error(f"Failed to track correction (non-blocking): {str(e)}")
            
            logger.info(f"Review submitted for violation {violation_id} by user {reviewer_user_id}: {action}")
            
            return {
                "review_id": str(review.id),
                "violation_id": str(violation_id),
                "action": action,
                "status": violation.status.value,
                "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error submitting review: {str(e)}")
            raise
    
    @staticmethod
    def assign_violation(
        db: Session,
        violation_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Assign a violation to a user."""
        try:
            # Get violation
            violation = db.query(Violation).filter(Violation.id == violation_id).first()
            if not violation:
                raise ValueError(f"Violation {violation_id} not found")
            
            # Get user
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Assign
            violation.assigned_to = user_id
            db.commit()
            
            logger.info(f"Violation {violation_id} assigned to user {user_id}")
            
            return {
                "violation_id": str(violation_id),
                "assigned_to": str(user_id),
                "assigned_user": user.to_dict()
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error assigning violation: {str(e)}")
            raise
    
    @staticmethod
    def get_review_history(
        db: Session,
        violation_id: str
    ) -> List[Dict[str, Any]]:
        """Get review history for a violation."""
        try:
            reviews = db.query(ViolationReview).filter(
                ViolationReview.violation_id == violation_id
            ).order_by(ViolationReview.reviewed_at.desc()).all()
            
            results = []
            for review in reviews:
                # Get reviewer info
                user = db.query(User).filter(User.id == review.reviewer_user_id).first()
                
                review_dict = {
                    "id": str(review.id),
                    "action": review.action.value,
                    "reason": review.reason,
                    "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
                    "reviewer": user.to_dict() if user else {"name": "Unknown", "email": review.reviewer_user_id}
                }
                results.append(review_dict)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting review history: {str(e)}")
            raise
    
    @staticmethod
    def get_my_reviews(
        db: Session,
        user_id: str,
        limit: int = 50
    ) -> Dict[str, Any]:
        """Get violations assigned to a specific user."""
        try:
            violations = db.query(Violation).filter(
                and_(
                    Violation.assigned_to == user_id,
                    Violation.status == ViolationStatus.PENDING_REVIEW
                )
            ).order_by(Violation.detected_at.desc()).limit(limit).all()
            
            results = []
            for violation in violations:
                results.append({
                    "id": str(violation.id),
                    "record_identifier": violation.record_identifier,
                    "severity": violation.severity,
                    "status": violation.status.value,
                    "justification": violation.justification,
                    "detected_at": violation.detected_at.isoformat() if violation.detected_at else None,
                    "risk_score": violation.risk_score
                })
            
            return {
                "violations": results,
                "count": len(results),
                "user_id": user_id
            }
            
        except Exception as e:
            logger.error(f"Error getting my reviews: {str(e)}")
            raise
    
    @staticmethod
    def get_review_statistics(db: Session) -> Dict[str, Any]:
        """Get review statistics."""
        try:
            # Total pending
            pending_count = db.query(Violation).filter(
                Violation.status == ViolationStatus.PENDING_REVIEW
            ).count()
            
            # Total confirmed
            confirmed_count = db.query(Violation).filter(
                Violation.status == ViolationStatus.CONFIRMED
            ).count()
            
            # Total dismissed
            dismissed_count = db.query(Violation).filter(
                Violation.status == ViolationStatus.DISMISSED
            ).count()
            
            # False positives
            false_positive_count = db.query(Violation).filter(
                Violation.is_false_positive == "true"
            ).count()
            
            # Assigned vs unassigned
            assigned_count = db.query(Violation).filter(
                and_(
                    Violation.assigned_to.isnot(None),
                    Violation.status == ViolationStatus.PENDING_REVIEW
                )
            ).count()
            
            unassigned_count = db.query(Violation).filter(
                and_(
                    Violation.assigned_to.is_(None),
                    Violation.status == ViolationStatus.PENDING_REVIEW
                )
            ).count()
            
            # Reviews by user
            reviews_by_user = db.query(
                User.name,
                func.count(ViolationReview.id).label('review_count')
            ).join(
                ViolationReview, User.id == ViolationReview.reviewer_user_id
            ).group_by(User.name).all()
            
            return {
                "pending_count": pending_count,
                "confirmed_count": confirmed_count,
                "dismissed_count": dismissed_count,
                "false_positive_count": false_positive_count,
                "assigned_count": assigned_count,
                "unassigned_count": unassigned_count,
                "reviews_by_user": [
                    {"name": name, "count": count} 
                    for name, count in reviews_by_user
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting review statistics: {str(e)}")
            raise
