"""Service for analyzing corrections and generating insights."""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.correction import Correction, CorrectedDecision
from src.models.user import User

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """Service for analyzing corrections and generating insights."""
    
    @staticmethod
    def get_overall_metrics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Calculate overall accuracy metrics."""
        try:
            query = db.query(Correction)
            
            # Apply date filters
            if start_date:
                query = query.filter(Correction.created_at >= start_date)
            if end_date:
                query = query.filter(Correction.created_at <= end_date)
            
            corrections = query.all()
            total = len(corrections)
            
            if total == 0:
                return {
                    "total_corrections": 0,
                    "accuracy": 0.0,
                    "false_positive_rate": 0.0,
                    "true_positive_rate": 0.0,
                    "needs_review_rate": 0.0,
                    "avg_confidence": 0.0
                }
            
            # Count by decision type
            true_positives = sum(1 for c in corrections if c.corrected_decision == CorrectedDecision.TRUE_POSITIVE)
            false_positives = sum(1 for c in corrections if c.corrected_decision == CorrectedDecision.FALSE_POSITIVE)
            needs_review = sum(1 for c in corrections if c.corrected_decision == CorrectedDecision.NEEDS_REVIEW)
            
            # Calculate confidence average
            confidences = [c.ai_confidence for c in corrections if c.ai_confidence is not None]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {
                "total_corrections": total,
                "accuracy": round(true_positives / total * 100, 2),
                "false_positive_rate": round(false_positives / total * 100, 2),
                "true_positive_rate": round(true_positives / total * 100, 2),
                "needs_review_rate": round(needs_review / total * 100, 2),
                "avg_confidence": round(avg_confidence, 3)
            }
            
        except Exception as e:
            logger.error(f"Error calculating overall metrics: {str(e)}")
            raise
    
    @staticmethod
    def get_rule_metrics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Calculate per-rule accuracy metrics."""
        try:
            query = db.query(Correction)
            
            # Apply date filters
            if start_date:
                query = query.filter(Correction.created_at >= start_date)
            if end_date:
                query = query.filter(Correction.created_at <= end_date)
            
            corrections = query.all()
            
            # Group by rule_id
            rules_data = {}
            for correction in corrections:
                rule_id = str(correction.rule_id)
                if rule_id not in rules_data:
                    rules_data[rule_id] = {
                        "rule_id": rule_id,
                        "rule_name": correction.rule_name,
                        "corrections": []
                    }
                rules_data[rule_id]["corrections"].append(correction)
            
            # Calculate metrics for each rule
            results = []
            for rule_id, data in rules_data.items():
                corrections_list = data["corrections"]
                total = len(corrections_list)
                
                true_positives = sum(1 for c in corrections_list if c.corrected_decision == CorrectedDecision.TRUE_POSITIVE)
                false_positives = sum(1 for c in corrections_list if c.corrected_decision == CorrectedDecision.FALSE_POSITIVE)
                needs_review = sum(1 for c in corrections_list if c.corrected_decision == CorrectedDecision.NEEDS_REVIEW)
                
                confidences = [c.ai_confidence for c in corrections_list if c.ai_confidence is not None]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                
                accuracy = (true_positives / total * 100) if total > 0 else 0.0
                fp_rate = (false_positives / total * 100) if total > 0 else 0.0
                
                # Determine trend
                trend = AnalyticsEngine._calculate_trend(corrections_list, total)
                
                results.append({
                    "rule_id": rule_id,
                    "rule_name": data["rule_name"],
                    "total_reviews": total,
                    "accuracy": round(accuracy, 2),
                    "false_positive_rate": round(fp_rate, 2),
                    "true_positive_count": true_positives,
                    "false_positive_count": false_positives,
                    "needs_review_count": needs_review,
                    "avg_confidence": round(avg_confidence, 3),
                    "trend": trend,
                    "high_fp_rate": fp_rate > 30
                })
            
            # Sort by total reviews descending
            results.sort(key=lambda x: x["total_reviews"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating rule metrics: {str(e)}")
            raise
    
    @staticmethod
    def get_correction_history(
        db: Session,
        limit: int = 100,
        offset: int = 0,
        rule_id: Optional[str] = None,
        reviewer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get paginated correction history with filters."""
        try:
            query = db.query(Correction)
            
            # Apply filters
            if rule_id:
                query = query.filter(Correction.rule_id == rule_id)
            if reviewer_id:
                query = query.filter(Correction.corrected_by == reviewer_id)
            if start_date:
                query = query.filter(Correction.created_at >= start_date)
            if end_date:
                query = query.filter(Correction.created_at <= end_date)
            
            # Get total count
            total_count = query.count()
            
            # Get paginated results
            corrections = query.order_by(
                Correction.created_at.desc()
            ).limit(limit).offset(offset).all()
            
            # Enrich with reviewer info
            results = []
            for correction in corrections:
                correction_dict = correction.to_dict()
                
                # Get reviewer info
                reviewer = db.query(User).filter(User.id == correction.corrected_by).first()
                if reviewer:
                    correction_dict["reviewer"] = reviewer.to_dict()
                
                results.append(correction_dict)
            
            return {
                "corrections": results,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            logger.error(f"Error getting correction history: {str(e)}")
            raise
    
    @staticmethod
    def get_improvement_suggestions(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Generate improvement suggestions based on correction patterns."""
        try:
            rule_metrics = AnalyticsEngine.get_rule_metrics(db, start_date, end_date)
            
            suggestions = []
            for metrics in rule_metrics:
                suggestion = AnalyticsEngine._generate_suggestion(metrics)
                if suggestion:
                    suggestions.append(suggestion)
            
            # Sort by priority
            priority_order = {"high": 0, "medium": 1, "low": 2}
            suggestions.sort(key=lambda x: priority_order.get(x["priority"], 3))
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating suggestions: {str(e)}")
            raise
    
    @staticmethod
    def get_trend_data(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        granularity: str = "day"
    ) -> List[Dict[str, Any]]:
        """Get time-series data for correction trends."""
        try:
            corrections = db.query(Correction).filter(
                and_(
                    Correction.created_at >= start_date,
                    Correction.created_at <= end_date
                )
            ).all()
            
            # Group by time period
            trends = {}
            for correction in corrections:
                if granularity == "day":
                    period = correction.created_at.date().isoformat()
                elif granularity == "week":
                    period = correction.created_at.isocalendar()[:2]
                    period = f"{period[0]}-W{period[1]}"
                else:  # month
                    period = correction.created_at.strftime("%Y-%m")
                
                if period not in trends:
                    trends[period] = {
                        "date": period,
                        "total_corrections": 0,
                        "true_positives": 0,
                        "false_positives": 0,
                        "needs_review": 0
                    }
                
                trends[period]["total_corrections"] += 1
                if correction.corrected_decision == CorrectedDecision.TRUE_POSITIVE:
                    trends[period]["true_positives"] += 1
                elif correction.corrected_decision == CorrectedDecision.FALSE_POSITIVE:
                    trends[period]["false_positives"] += 1
                else:
                    trends[period]["needs_review"] += 1
            
            # Calculate accuracy for each period
            results = []
            for period, data in sorted(trends.items()):
                total = data["total_corrections"]
                accuracy = (data["true_positives"] / total * 100) if total > 0 else 0.0
                data["accuracy"] = round(accuracy, 2)
                results.append(data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting trend data: {str(e)}")
            raise
    
    @staticmethod
    def get_reviewer_statistics(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Calculate per-reviewer statistics."""
        try:
            query = db.query(Correction)
            
            if start_date:
                query = query.filter(Correction.created_at >= start_date)
            if end_date:
                query = query.filter(Correction.created_at <= end_date)
            
            corrections = query.all()
            
            # Group by reviewer
            reviewers_data = {}
            for correction in corrections:
                reviewer_id = str(correction.corrected_by)
                if reviewer_id not in reviewers_data:
                    reviewers_data[reviewer_id] = {
                        "corrections": [],
                        "reviewer_id": reviewer_id
                    }
                reviewers_data[reviewer_id]["corrections"].append(correction)
            
            # Calculate stats for each reviewer
            results = []
            for reviewer_id, data in reviewers_data.items():
                corrections_list = data["corrections"]
                total = len(corrections_list)
                
                confirm_count = sum(1 for c in corrections_list if c.corrected_decision == CorrectedDecision.TRUE_POSITIVE)
                dismiss_count = sum(1 for c in corrections_list if c.corrected_decision == CorrectedDecision.FALSE_POSITIVE)
                request_info_count = sum(1 for c in corrections_list if c.corrected_decision == CorrectedDecision.NEEDS_REVIEW)
                
                # Get reviewer info
                reviewer = db.query(User).filter(User.id == reviewer_id).first()
                reviewer_name = reviewer.name if reviewer else "Unknown"
                
                results.append({
                    "reviewer_id": reviewer_id,
                    "reviewer_name": reviewer_name,
                    "total_reviews": total,
                    "confirm_count": confirm_count,
                    "dismiss_count": dismiss_count,
                    "request_info_count": request_info_count
                })
            
            # Sort by total reviews
            results.sort(key=lambda x: x["total_reviews"], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting reviewer statistics: {str(e)}")
            raise
    
    @staticmethod
    def _calculate_trend(corrections: List[Correction], total_reviews: int) -> str:
        """Determine trend direction based on recent vs older corrections."""
        if total_reviews < 10:
            return "insufficient_data"
        
        # Sort by date
        sorted_corrections = sorted(corrections, key=lambda c: c.created_at)
        
        # Split into two halves
        mid = len(sorted_corrections) // 2
        older_half = sorted_corrections[:mid]
        recent_half = sorted_corrections[mid:]
        
        # Calculate accuracy for each half
        older_tp = sum(1 for c in older_half if c.corrected_decision == CorrectedDecision.TRUE_POSITIVE)
        recent_tp = sum(1 for c in recent_half if c.corrected_decision == CorrectedDecision.TRUE_POSITIVE)
        
        older_accuracy = (older_tp / len(older_half) * 100) if older_half else 0
        recent_accuracy = (recent_tp / len(recent_half) * 100) if recent_half else 0
        
        diff = recent_accuracy - older_accuracy
        
        if diff > 10:
            return "improving"
        elif diff < -10:
            return "declining"
        else:
            return "stable"
    
    @staticmethod
    def _generate_suggestion(rule_metrics: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate improvement suggestion for a rule based on its metrics."""
        rule_id = rule_metrics["rule_id"]
        rule_name = rule_metrics["rule_name"]
        fp_rate = rule_metrics["false_positive_rate"]
        total_reviews = rule_metrics["total_reviews"]
        trend = rule_metrics["trend"]
        avg_confidence = rule_metrics["avg_confidence"]
        
        # Check for issues
        if total_reviews < 10:
            return {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "issue": "Insufficient data for analysis",
                "suggestion": "Collect more data before drawing conclusions",
                "priority": "low",
                "metrics": rule_metrics
            }
        
        if fp_rate > 40:
            return {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "issue": f"Very high false positive rate ({fp_rate}%)",
                "suggestion": "Review and refine rule definition",
                "priority": "high",
                "metrics": rule_metrics
            }
        
        if trend == "declining":
            return {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "issue": "Accuracy declining over time",
                "suggestion": "Investigate recent changes or data drift",
                "priority": "high",
                "metrics": rule_metrics
            }
        
        if avg_confidence < 0.5 and fp_rate > 30:
            return {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "issue": f"Low confidence with high false positives ({fp_rate}%)",
                "suggestion": "Adjust confidence threshold for this rule",
                "priority": "medium",
                "metrics": rule_metrics
            }
        
        if avg_confidence > 0.8 and fp_rate > 30:
            return {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "issue": f"High confidence but high false positives ({fp_rate}%)",
                "suggestion": "Rule may need significant revision",
                "priority": "high",
                "metrics": rule_metrics
            }
        
        if fp_rate > 30:
            return {
                "rule_id": rule_id,
                "rule_name": rule_name,
                "issue": f"Elevated false positive rate ({fp_rate}%)",
                "suggestion": "Consider rule refinement",
                "priority": "medium",
                "metrics": rule_metrics
            }
        
        return None
