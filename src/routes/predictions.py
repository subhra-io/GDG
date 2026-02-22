"""API routes for predictive analytics and risk analysis."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from src.core.database import get_db
from src.services.predictive_analytics import (
    get_predictor,
    get_high_risk_records,
    simulate_what_if
)
from src.models.prediction import Prediction

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/predictions", tags=["predictions"])


class PredictionRequest(BaseModel):
    """Request model for violation prediction."""
    record: Dict[str, Any]
    policy_id: Optional[str] = None


class WhatIfRequest(BaseModel):
    """Request model for what-if simulation."""
    record: Dict[str, Any]
    changes: Dict[str, Any]


@router.post("/train")
async def train_model(
    policy_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Train the ML model on historical violations.
    
    - **policy_id**: Optional policy ID to train on specific policy violations
    """
    try:
        predictor = get_predictor()
        result = predictor.train_model(db, policy_id)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predict")
async def predict_violation(
    request: PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict violation probability for a record.
    
    - **record**: Record data to analyze
    - **policy_id**: Optional policy ID for context
    """
    try:
        predictor = get_predictor()
        prediction = predictor.predict_violation(request.record)
        
        # Save prediction to database
        db_prediction = Prediction(
            record_id=request.record.get('transaction_id', 'unknown'),
            policy_id=request.policy_id,
            violation_probability=prediction['violation_probability'],
            confidence_score=prediction['confidence_score'],
            risk_level=prediction['risk_level'],
            risk_factors=prediction['risk_factors'],
            recommendations=prediction['recommendations'],
            model_version=prediction['model_version']
        )
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        
        return {
            **prediction,
            "prediction_id": str(db_prediction.id),
            "record_id": db_prediction.record_id
        }
        
    except Exception as e:
        logger.error(f"Error predicting violation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/risk-score/{record_id}")
async def get_risk_score(
    record_id: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest risk score for a specific record.
    
    - **record_id**: ID of the record to get risk score for
    """
    try:
        # Get latest prediction for this record
        prediction = db.query(Prediction).filter(
            Prediction.record_id == record_id
        ).order_by(Prediction.predicted_at.desc()).first()
        
        if not prediction:
            raise HTTPException(
                status_code=404,
                detail=f"No prediction found for record {record_id}"
            )
        
        return prediction.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting risk score: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/high-risk-records")
async def get_high_risk(
    policy_id: Optional[str] = None,
    threshold: float = Query(0.6, ge=0.0, le=1.0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Get list of high-risk records.
    
    - **policy_id**: Optional policy ID to filter by
    - **threshold**: Minimum probability threshold (default: 0.6)
    - **limit**: Maximum number of records to return (default: 50)
    """
    try:
        records = await get_high_risk_records(db, policy_id, threshold, limit)
        
        return {
            "high_risk_records": records,
            "total_count": len(records),
            "threshold": threshold,
            "policy_id": policy_id
        }
        
    except Exception as e:
        logger.error(f"Error getting high-risk records: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/what-if")
async def what_if_simulation(request: WhatIfRequest):
    """
    Simulate what-if scenario by modifying record parameters.
    
    - **record**: Original record data
    - **changes**: Changes to apply to the record
    
    Example:
    ```json
    {
        "record": {"amount": 50000, "approver_1": null},
        "changes": {"approver_1": "EMP001", "approver_2": "EMP002"}
    }
    ```
    """
    try:
        result = await simulate_what_if(request.record, request.changes)
        return result
        
    except Exception as e:
        logger.error(f"Error in what-if simulation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_prediction_statistics(
    policy_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get prediction statistics and model performance metrics.
    
    - **policy_id**: Optional policy ID to filter by
    """
    try:
        from sqlalchemy import func
        
        # Base query
        query = db.query(Prediction)
        if policy_id:
            query = query.filter(Prediction.policy_id == policy_id)
        
        # Get statistics
        total_predictions = query.count()
        
        # Risk level distribution
        risk_distribution = {}
        for level in ['low', 'medium', 'high', 'critical']:
            count = query.filter(Prediction.risk_level == level).count()
            risk_distribution[level] = count
        
        # Average probability by risk level
        avg_probability = db.query(
            Prediction.risk_level,
            func.avg(Prediction.violation_probability).label('avg_prob')
        ).group_by(Prediction.risk_level).all()
        
        avg_prob_by_level = {level: float(prob) for level, prob in avg_probability}
        
        # Model accuracy (where actual outcome is known)
        accurate_predictions = query.filter(
            Prediction.actual_violation.isnot(None),
            Prediction.prediction_accuracy >= 0.8
        ).count()
        
        total_with_outcome = query.filter(
            Prediction.actual_violation.isnot(None)
        ).count()
        
        accuracy = (accurate_predictions / total_with_outcome * 100) if total_with_outcome > 0 else None
        
        return {
            "total_predictions": total_predictions,
            "risk_distribution": risk_distribution,
            "average_probability_by_level": avg_prob_by_level,
            "model_accuracy": accuracy,
            "predictions_with_outcome": total_with_outcome,
            "policy_id": policy_id
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/model-info")
async def get_model_info():
    """Get information about the current ML model."""
    try:
        predictor = get_predictor()
        
        return {
            "model_type": "RandomForestClassifier",
            "is_trained": predictor.is_trained,
            "model_version": predictor.model_version,
            "feature_count": len(predictor.feature_names),
            "features": predictor.feature_names,
            "n_estimators": predictor.model.n_estimators,
            "max_depth": predictor.model.max_depth
        }
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
