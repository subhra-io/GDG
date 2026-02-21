"""Risk scoring engine for violations."""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.core.logging import get_logger
from src.models import Violation

logger = get_logger(__name__)


class RiskScoringEngine:
    """Calculate risk scores for violations."""
    
    SEVERITY_WEIGHTS = {
        "critical": 40,
        "high": 30,
        "medium": 20,
        "low": 10
    }
    
    RISK_LEVELS = {
        "Low": (0, 25),
        "Medium": (26, 50),
        "High": (51, 75),
        "Critical": (76, 100)
    }
    
    def calculate_risk_score(
        self,
        violation: Violation,
        record: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk score.
        
        Factors:
        - Severity weight: critical=40, high=30, medium=20, low=10
        - Transaction amount: normalized 0-25 points
        - Frequency: repeat violations add 0-20 points
        - Historical patterns: similar violations add 0-15 points
        
        Args:
            violation: The violation object
            record: The record data
            db: Database session for historical queries
            
        Returns:
            Dict with score (0-100), level, and breakdown
        """
        try:
            # Base severity score
            severity = violation.severity.lower()
            severity_score = self.SEVERITY_WEIGHTS.get(severity, 10)
            
            # Amount factor (0-25 points)
            amount_score = self._calculate_amount_factor(record)
            
            # Frequency factor (0-20 points)
            frequency_score = self._calculate_frequency_factor(
                violation, db
            )
            
            # Historical pattern factor (0-15 points)
            historical_score = self._calculate_historical_factor(
                violation, db
            )
            
            # Total score (capped at 100)
            total_score = min(
                100,
                severity_score + amount_score + frequency_score + historical_score
            )
            
            # Determine risk level
            risk_level = self.get_risk_level(total_score)
            
            risk_data = {
                "score": total_score,
                "level": risk_level,
                "factors": {
                    "severity_weight": severity_score,
                    "amount_factor": amount_score,
                    "frequency_factor": frequency_score,
                    "historical_factor": historical_score
                }
            }
            
            logger.info(
                "Risk score calculated",
                violation_id=str(violation.id),
                score=total_score,
                level=risk_level
            )
            
            return risk_data
            
        except Exception as e:
            logger.error(
                "Error calculating risk score",
                error=str(e),
                violation_id=str(violation.id)
            )
            # Return default low risk on error
            return {
                "score": 10,
                "level": "Low",
                "factors": {
                    "severity_weight": 10,
                    "amount_factor": 0,
                    "frequency_factor": 0,
                    "historical_factor": 0
                }
            }
    
    def _calculate_amount_factor(self, record: Dict[str, Any]) -> int:
        """
        Calculate risk factor based on transaction amount.
        
        Returns 0-25 points based on amount thresholds.
        """
        # Try to find amount field in record
        amount = None
        for key in ["amount", "transaction_amount", "value", "total"]:
            if key in record:
                try:
                    amount = float(record[key])
                    break
                except (ValueError, TypeError):
                    continue
        
        if amount is None:
            return 0
        
        # Score based on amount thresholds
        if amount >= 1000000:  # $1M+
            return 25
        elif amount >= 500000:  # $500K+
            return 20
        elif amount >= 100000:  # $100K+
            return 15
        elif amount >= 50000:   # $50K+
            return 10
        elif amount >= 10000:   # $10K+
            return 5
        else:
            return 0
    
    def _calculate_frequency_factor(
        self,
        violation: Violation,
        db: Session
    ) -> int:
        """
        Calculate risk factor based on violation frequency.
        
        Returns 0-20 points based on repeat violations.
        """
        try:
            # Count violations for same record in last 30 days
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            
            repeat_count = db.query(Violation).filter(
                Violation.record_identifier == violation.record_identifier,
                Violation.detected_at >= thirty_days_ago,
                Violation.id != violation.id
            ).count()
            
            # Score based on frequency
            if repeat_count >= 5:
                return 20
            elif repeat_count >= 3:
                return 15
            elif repeat_count >= 2:
                return 10
            elif repeat_count >= 1:
                return 5
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"Error calculating frequency factor: {e}")
            return 0
    
    def _calculate_historical_factor(
        self,
        violation: Violation,
        db: Session
    ) -> int:
        """
        Calculate risk factor based on historical patterns.
        
        Returns 0-15 points based on similar past violations.
        """
        try:
            # Count similar violations (same rule) in last 90 days
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            
            similar_count = db.query(Violation).filter(
                Violation.rule_id == violation.rule_id,
                Violation.detected_at >= ninety_days_ago,
                Violation.id != violation.id
            ).count()
            
            # Score based on pattern
            if similar_count >= 10:
                return 15
            elif similar_count >= 5:
                return 10
            elif similar_count >= 2:
                return 5
            else:
                return 0
                
        except Exception as e:
            logger.warning(f"Error calculating historical factor: {e}")
            return 0
    
    def get_risk_level(self, score: int) -> str:
        """
        Map score to risk level: Low/Medium/High/Critical.
        
        Args:
            score: Risk score (0-100)
            
        Returns:
            Risk level string
        """
        for level, (min_score, max_score) in self.RISK_LEVELS.items():
            if min_score <= score <= max_score:
                return level
        return "Low"  # Default
    
    def calculate_risk_trend(
        self,
        db: Session,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Calculate risk trend over time period.
        
        Args:
            db: Database session
            days: Number of days to analyze
            
        Returns:
            List of daily risk data points
        """
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Query violations grouped by date
            results = db.query(
                func.date(Violation.detected_at).label('date'),
                func.avg(Violation.risk_score).label('avg_risk'),
                func.count(Violation.id).label('count')
            ).filter(
                Violation.detected_at >= start_date,
                Violation.risk_score.isnot(None)
            ).group_by(
                func.date(Violation.detected_at)
            ).order_by(
                func.date(Violation.detected_at)
            ).all()
            
            trend_data = []
            for row in results:
                trend_data.append({
                    "date": row.date.isoformat(),
                    "average_risk": round(row.avg_risk, 2) if row.avg_risk else 0,
                    "violation_count": row.count
                })
            
            return trend_data
            
        except Exception as e:
            logger.error(f"Error calculating risk trend: {e}")
            return []
