"""Violation detection service."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re

from src.core.logging import get_logger

logger = get_logger(__name__)


class ViolationDetector:
    """Detect violations by evaluating records against rules."""
    
    def __init__(self):
        """Initialize violation detector."""
        pass
    
    def evaluate_record(
        self,
        record: Dict[str, Any],
        rule: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate a single record against a rule.
        
        Args:
            record: Record data to evaluate
            rule: Compliance rule with validation logic
            
        Returns:
            Violation details if rule is violated, None otherwise
        """
        try:
            validation_logic = rule.get("validation_logic", {})
            
            # Extract condition from validation logic
            condition = validation_logic.get("condition", {})
            if not condition:
                logger.warning("Rule has no condition", rule_id=rule.get("id"))
                return None
            
            # Evaluate the condition
            is_violation = self._evaluate_condition(record, condition)
            
            if is_violation:
                return {
                    "rule_id": rule["id"],
                    "record_identifier": str(record.get("id", "unknown")),
                    "violation_details": {
                        "expected": condition,
                        "actual": self._extract_actual_values(record, condition)
                    }
                }
            
            return None
            
        except Exception as e:
            logger.error(
                "Error evaluating record",
                error=str(e),
                rule_id=rule.get("id")
            )
            return None
    
    def _evaluate_condition(
        self,
        record: Dict[str, Any],
        condition: Dict[str, Any]
    ) -> bool:
        """
        Evaluate a condition against a record.
        
        Args:
            record: Record data
            condition: Condition to evaluate
            
        Returns:
            True if condition is violated (fails)
        """
        field = condition.get("field")
        operator = condition.get("operator")
        expected_value = condition.get("value")
        
        if not field or not operator:
            return False
        
        # Get actual value from record (support nested fields)
        actual_value = self._get_nested_value(record, field)
        
        if actual_value is None:
            # Missing field might be a violation depending on the rule
            return operator == "is_not_null"
        
        # Evaluate based on operator
        if operator == "greater_than":
            try:
                return float(actual_value) > float(expected_value)
            except (ValueError, TypeError):
                return False
        
        elif operator == "less_than":
            try:
                return float(actual_value) < float(expected_value)
            except (ValueError, TypeError):
                return False
        
        elif operator == "equals":
            return str(actual_value) == str(expected_value)
        
        elif operator == "not_equals":
            return str(actual_value) != str(expected_value)
        
        elif operator == "contains":
            return str(expected_value).lower() in str(actual_value).lower()
        
        elif operator == "not_contains":
            return str(expected_value).lower() not in str(actual_value).lower()
        
        elif operator == "regex_match":
            try:
                pattern = re.compile(expected_value)
                return bool(pattern.search(str(actual_value)))
            except re.error:
                return False
        
        elif operator == "is_null":
            return actual_value is None
        
        elif operator == "is_not_null":
            return actual_value is not None
        
        return False
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Get value from nested dictionary using dot notation.
        
        Args:
            data: Dictionary to search
            field_path: Field path (e.g., "data.amount" or "amount")
            
        Returns:
            Field value or None if not found
        """
        keys = field_path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _extract_actual_values(
        self,
        record: Dict[str, Any],
        condition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract actual values from record for violation details.
        
        Args:
            record: Record data
            condition: Condition that was evaluated
            
        Returns:
            Dictionary of actual values
        """
        field = condition.get("field")
        if not field:
            return {}
        
        actual_value = self._get_nested_value(record, field)
        
        return {
            "field": field,
            "value": actual_value
        }
    
    def calculate_risk_score(self, violations: List[Dict[str, Any]]) -> int:
        """
        Calculate risk score based on violations.
        
        Args:
            violations: List of violations
            
        Returns:
            Risk score (0-100, where 100 is perfect compliance)
        """
        if not violations:
            return 100
        
        # Count violations by severity
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for violation in violations:
            severity = violation.get("severity", "low").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1
        
        # Calculate penalty
        penalty = (
            severity_counts["critical"] * 10 +
            severity_counts["high"] * 5 +
            severity_counts["medium"] * 2 +
            severity_counts["low"] * 1
        )
        
        # Calculate score (minimum 0)
        score = max(0, 100 - penalty)
        
        logger.info(
            "Risk score calculated",
            score=score,
            violations=len(violations),
            severity_counts=severity_counts
        )
        
        return score
