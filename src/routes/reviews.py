"""API routes for human review workflow."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from src.core.database import get_db
from src.services.review_service import ReviewService
from src.models.user import User, UserRole

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/reviews", tags=["reviews"])


class ReviewSubmission(BaseModel):
    """Request model for submitting a review."""
    reviewer_user_id: str
    action: str  # 'confirm', 'dismiss', 'request_more_info'
    reason: Optional[str] = None


class AssignmentRequest(BaseModel):
    """Request model for assigning a violation."""
    user_id: str


@router.get("/queue")
async def get_review_queue(
    status: Optional[str] = None,
    assigned_to: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get review queue of violations pending review.
    
    - **status**: Filter by status (pending_review, confirmed, dismissed)
    - **assigned_to**: Filter by assigned user ID
    - **severity**: Filter by severity (critical, high, medium, low)
    - **limit**: Maximum number of results
    - **offset**: Pagination offset
    """
    try:
        result = ReviewService.get_review_queue(
            db, status, assigned_to, severity, limit, offset
        )
        return result
        
    except Exception as e:
        logger.error(f"Error getting review queue: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{violation_id}")
async def submit_review(
    violation_id: str,
    review: ReviewSubmission,
    db: Session = Depends(get_db)
):
    """
    Submit a review action for a violation.
    
    - **violation_id**: ID of the violation to review
    - **reviewer_user_id**: ID of the user submitting the review
    - **action**: Review action (confirm, dismiss, request_more_info)
    - **reason**: Optional reason/comment for the action
    """
    try:
        result = ReviewService.submit_review(
            db,
            violation_id,
            review.reviewer_user_id,
            review.action,
            review.reason
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting review: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{violation_id}/assign")
async def assign_violation(
    violation_id: str,
    assignment: AssignmentRequest,
    db: Session = Depends(get_db)
):
    """
    Assign a violation to a user for review.
    
    - **violation_id**: ID of the violation to assign
    - **user_id**: ID of the user to assign to
    """
    try:
        result = ReviewService.assign_violation(
            db,
            violation_id,
            assignment.user_id
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error assigning violation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{violation_id}/history")
async def get_review_history(
    violation_id: str,
    db: Session = Depends(get_db)
):
    """
    Get review history for a specific violation.
    
    - **violation_id**: ID of the violation
    """
    try:
        history = ReviewService.get_review_history(db, violation_id)
        return {
            "violation_id": violation_id,
            "history": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"Error getting review history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-reviews/{user_id}")
async def get_my_reviews(
    user_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get violations assigned to a specific user.
    
    - **user_id**: ID of the user
    - **limit**: Maximum number of results
    """
    try:
        result = ReviewService.get_my_reviews(db, user_id, limit)
        return result
        
    except Exception as e:
        logger.error(f"Error getting my reviews: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_review_statistics(db: Session = Depends(get_db)):
    """
    Get review statistics and metrics.
    
    Returns counts for pending, confirmed, dismissed violations,
    false positives, assigned/unassigned, and reviews by user.
    """
    try:
        stats = ReviewService.get_review_statistics(db)
        return stats
        
    except Exception as e:
        logger.error(f"Error getting review statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# User management endpoints

@router.get("/users")
async def get_users(
    role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of users.
    
    - **role**: Optional filter by role (admin, reviewer, viewer)
    """
    try:
        query = db.query(User)
        
        if role:
            try:
                user_role = UserRole(role)
                query = query.filter(User.role == user_role)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        
        users = query.all()
        
        return {
            "users": [user.to_dict() for user in users],
            "count": len(users)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users")
async def create_user(
    email: str,
    name: str,
    role: str = "reviewer",
    db: Session = Depends(get_db)
):
    """
    Create a new user.
    
    - **email**: User email (must be unique)
    - **name**: User full name
    - **role**: User role (admin, reviewer, viewer)
    """
    try:
        # Validate role
        try:
            user_role = UserRole(role)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
        
        # Check if user exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(status_code=400, detail=f"User with email {email} already exists")
        
        # Create user
        user = User(
            email=email,
            name=name,
            role=user_role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        logger.info(f"Created user: {email}")
        
        return user.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
