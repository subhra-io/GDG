"""Predictive analytics service for violation prediction using ML."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.models.violation import Violation
from src.models.rule import ComplianceRule
from src.models.prediction import Prediction

logger = logging.getLogger(__name__)


class ViolationPredictor:
    """ML-based violation predictor."""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = []
        self.model_version = "1.0"
    
    def extract_features(self, record: Dict[str, Any]) -> Dict[str, float]:
        """Extract numerical features from a record."""
        features = {}
        
        # Amount-based features
        if 'amount' in record:
            features['amount'] = float(record['amount'])
            features['amount_log'] = np.log1p(float(record['amount']))
        
        # Approval features
        features['has_approver_1'] = 1.0 if record.get('approver_1') else 0.0
        features['has_approver_2'] = 1.0 if record.get('approver_2') else 0.0
        features['approval_count'] = sum([
            1 for k in ['approver_1', 'approver_2'] 
            if record.get(k)
        ])
        
        # Transaction features
        features['has_transaction_id'] = 1.0 if record.get('transaction_id') else 0.0
        features['has_customer_id'] = 1.0 if record.get('customer_id') else 0.0
        
        # Same person features
        if record.get('initiator') and record.get('approver_1'):
            features['same_initiator_approver'] = 1.0 if record['initiator'] == record['approver_1'] else 0.0
        else:
            features['same_initiator_approver'] = 0.0
        
        return features
    
    def train_model(self, db: Session, policy_id: Optional[str] = None) -> Dict[str, Any]:
        """Train the ML model on historical violations."""
        try:
            logger.info("Training violation prediction model...")
            
            # Get historical violations
            query = db.query(Violation)
            if policy_id:
                query = query.filter(Violation.policy_id == policy_id)
            
            violations = query.all()
            
            if len(violations) < 10:
                logger.warning(f"Not enough data to train model: {len(violations)} violations")
                return {
                    "success": False,
                    "message": "Not enough historical data (minimum 10 violations required)",
                    "violations_count": len(violations)
                }
            
            # Prepare training data
            X_data = []
            y_data = []
            
            for violation in violations:
                if violation.record_snapshot:
                    features = self.extract_features(violation.record_snapshot)
                    X_data.append(list(features.values()))
                    y_data.append(1)  # Violation occurred
                    
                    # Store feature names from first record
                    if not self.feature_names:
                        self.feature_names = list(features.keys())
            
            # Add some non-violation examples (synthetic for now)
            # In production, you'd have actual non-violation records
            for _ in range(len(violations) // 2):
                # Create synthetic "good" records
                good_record = {
                    'amount': np.random.uniform(1000, 20000),
                    'approver_1': 'EMP001',
                    'approver_2': 'EMP002',
                    'initiator': 'EMP003',
                    'transaction_id': 'TXN001',
                    'customer_id': 'CUST001'
                }
                features = self.extract_features(good_record)
                X_data.append(list(features.values()))
                y_data.append(0)  # No violation
            
            # Convert to numpy arrays
            X = np.array(X_data)
            y = np.array(y_data)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model
            self.model.fit(X_scaled, y)
            self.is_trained = True
            
            # Calculate training accuracy
            train_accuracy = self.model.score(X_scaled, y)
            
            logger.info(f"Model trained successfully. Accuracy: {train_accuracy:.2%}")
            
            return {
                "success": True,
                "message": "Model trained successfully",
                "violations_count": len(violations),
                "training_samples": len(X),
                "accuracy": train_accuracy,
                "feature_count": len(self.feature_names),
                "features": self.feature_names
            }
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            return {
                "success": False,
                "message": f"Training failed: {str(e)}"
            }
    
    def predict_violation(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Predict violation probability for a record."""
        try:
            if not self.is_trained:
                # Return rule-based prediction if model not trained
                return self._rule_based_prediction(record)
            
            # Extract features
            features = self.extract_features(record)
            
            # Ensure feature order matches training
            X = np.array([[features.get(name, 0.0) for name in self.feature_names]])
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            probability = self.model.predict_proba(X_scaled)[0][1]  # Probability of violation
            confidence = max(self.model.predict_proba(X_scaled)[0])  # Confidence in prediction
            
            # Determine risk level
            if probability >= 0.8:
                risk_level = "critical"
            elif probability >= 0.6:
                risk_level = "high"
            elif probability >= 0.4:
                risk_level = "medium"
            else:
                risk_level = "low"
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(record, features)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(risk_factors, probability)
            
            return {
                "violation_probability": float(probability),
                "confidence_score": float(confidence),
                "risk_level": risk_level,
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "model_version": self.model_version,
                "prediction_method": "ml_model"
            }
            
        except Exception as e:
            logger.error(f"Error predicting violation: {str(e)}")
            return self._rule_based_prediction(record)
    
    def _rule_based_prediction(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback rule-based prediction when ML model is not available."""
        risk_factors = []
        probability = 0.0
        
        # Check amount
        amount = float(record.get('amount', 0))
        if amount > 25000:
            risk_factors.append("Transaction amount exceeds $25,000 threshold")
            probability += 0.3
        
        # Check dual authorization
        if not record.get('approver_1') or not record.get('approver_2'):
            risk_factors.append("Missing dual authorization")
            probability += 0.4
        
        # Check segregation of duties
        if record.get('initiator') == record.get('approver_1'):
            risk_factors.append("Same person as initiator and approver")
            probability += 0.3
        
        # Cap probability at 1.0
        probability = min(probability, 1.0)
        
        # Determine risk level
        if probability >= 0.8:
            risk_level = "critical"
        elif probability >= 0.6:
            risk_level = "high"
        elif probability >= 0.4:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        recommendations = self._generate_recommendations(risk_factors, probability)
        
        return {
            "violation_probability": probability,
            "confidence_score": 0.7,  # Lower confidence for rule-based
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "model_version": self.model_version,
            "prediction_method": "rule_based"
        }
    
    def _identify_risk_factors(self, record: Dict[str, Any], features: Dict[str, float]) -> List[str]:
        """Identify specific risk factors from record and features."""
        risk_factors = []
        
        # Amount-based risks
        amount = float(record.get('amount', 0))
        if amount > 25000:
            risk_factors.append(f"High transaction amount: ${amount:,.2f}")
        
        # Approval risks
        if features.get('approval_count', 0) < 2:
            risk_factors.append("Insufficient approvals (requires dual authorization)")
        
        if features.get('same_initiator_approver', 0) == 1.0:
            risk_factors.append("Segregation of duties violation (same initiator and approver)")
        
        # Missing data risks
        if not record.get('transaction_id'):
            risk_factors.append("Missing transaction ID")
        
        if not record.get('customer_id'):
            risk_factors.append("Missing customer ID")
        
        return risk_factors
    
    def _generate_recommendations(self, risk_factors: List[str], probability: float) -> List[str]:
        """Generate preventive recommendations based on risk factors."""
        recommendations = []
        
        if probability >= 0.8:
            recommendations.append("🚨 URGENT: Immediate review required before processing")
        
        if any("amount" in factor.lower() for factor in risk_factors):
            recommendations.append("Require additional approval for high-value transactions")
            recommendations.append("Implement transaction amount limits")
        
        if any("authorization" in factor.lower() for factor in risk_factors):
            recommendations.append("Enforce dual authorization policy")
            recommendations.append("Add automated approval workflow")
        
        if any("segregation" in factor.lower() or "same" in factor.lower() for factor in risk_factors):
            recommendations.append("Enforce segregation of duties checks")
            recommendations.append("Prevent same person from multiple roles")
        
        if any("missing" in factor.lower() for factor in risk_factors):
            recommendations.append("Make all required fields mandatory")
            recommendations.append("Implement data validation checks")
        
        if probability >= 0.6:
            recommendations.append("Flag for manual compliance review")
        
        return recommendations


# Global predictor instance
_predictor = ViolationPredictor()


def get_predictor() -> ViolationPredictor:
    """Get the global predictor instance."""
    return _predictor


async def get_high_risk_records(
    db: Session,
    policy_id: Optional[str] = None,
    threshold: float = 0.6,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get records with high violation probability."""
    try:
        predictor = get_predictor()
        
        # Get recent predictions
        query = db.query(Prediction).filter(
            Prediction.violation_probability >= threshold
        ).order_by(Prediction.violation_probability.desc())
        
        if policy_id:
            query = query.filter(Prediction.policy_id == policy_id)
        
        predictions = query.limit(limit).all()
        
        return [pred.to_dict() for pred in predictions]
        
    except Exception as e:
        logger.error(f"Error getting high-risk records: {str(e)}")
        return []


async def simulate_what_if(
    record: Dict[str, Any],
    changes: Dict[str, Any]
) -> Dict[str, Any]:
    """Simulate what-if scenario by modifying record and predicting."""
    try:
        predictor = get_predictor()
        
        # Create modified record
        modified_record = record.copy()
        modified_record.update(changes)
        
        # Get predictions for both
        original_prediction = predictor.predict_violation(record)
        modified_prediction = predictor.predict_violation(modified_record)
        
        # Calculate impact
        probability_change = modified_prediction['violation_probability'] - original_prediction['violation_probability']
        risk_change = "increased" if probability_change > 0 else "decreased" if probability_change < 0 else "unchanged"
        
        return {
            "original": original_prediction,
            "modified": modified_prediction,
            "changes_applied": changes,
            "impact": {
                "probability_change": probability_change,
                "risk_change": risk_change,
                "risk_level_change": f"{original_prediction['risk_level']} → {modified_prediction['risk_level']}"
            }
        }
        
    except Exception as e:
        logger.error(f"Error in what-if simulation: {str(e)}")
        raise
