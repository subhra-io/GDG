"""Production-ready prompt templates for rule extraction."""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class RuleExtractionPrompt:
    """Production prompt template for extracting compliance rules from policy documents."""
    
    SYSTEM_PROMPT = """You are an expert compliance analyst specializing in extracting actionable rules from policy documents.

Your task is to identify rules that can be validated against database records. Focus on:
- Quantitative thresholds (amounts, counts, percentages)
- Time-based constraints (within X hours/days)
- Pattern requirements (frequency, sequences)
- Required field validations
- Conditional logic (if-then rules)

Return structured JSON that can be directly used for automated compliance checking."""

    @staticmethod
    def build_extraction_prompt(policy_text: str) -> str:
        """
        Build the user prompt for rule extraction.
        
        Args:
            policy_text: The policy document text
            
        Returns:
            Formatted prompt string
        """
        return f"""Extract all actionable compliance rules from this policy document.

POLICY DOCUMENT:
{policy_text}

INSTRUCTIONS:
1. Identify rules that can be validated against data records
2. Extract specific thresholds, limits, and conditions
3. Determine the severity based on language (must/critical/required = high/critical, should = medium, may = low)
4. Provide confidence scores based on clarity and specificity

RETURN FORMAT (JSON):
{{
  "rules": [
    {{
      "rule_id": "R001",
      "description": "Clear, actionable description of what the rule enforces",
      "category": "transaction_limit|pattern_detection|required_field|time_constraint|other",
      "condition": {{
        "field": "field_name (e.g., amount, transaction_type)",
        "operator": "greater_than|less_than|equals|not_equals|contains|not_contains|regex_match|between",
        "value": "threshold value or pattern",
        "additional_conditions": [
          {{
            "field": "secondary_field",
            "operator": "operator",
            "value": "value"
          }}
        ],
        "logic": "AND|OR (for multiple conditions)"
      }},
      "severity": "critical|high|medium|low",
      "page_reference": "page number or section",
      "confidence_score": 0.95,
      "validation_query": "SQL-like description of how to check this rule"
    }}
  ],
  "metadata": {{
    "total_rules_found": 4,
    "policy_type": "AML|GDPR|SOX|HIPAA|other",
    "extraction_notes": "Any ambiguities or clarifications needed"
  }}
}}

EXAMPLES OF GOOD RULES:

Example 1 - Transaction Limit:
{{
  "rule_id": "R001",
  "description": "Single transactions exceeding $10,000 must be flagged for review",
  "category": "transaction_limit",
  "condition": {{
    "field": "amount",
    "operator": "greater_than",
    "value": 10000,
    "logic": "AND"
  }},
  "severity": "high",
  "page_reference": "Page 3, Section 2.1",
  "confidence_score": 0.98,
  "validation_query": "SELECT * FROM transactions WHERE amount > 10000"
}}

Example 2 - Pattern Detection:
{{
  "rule_id": "R002",
  "description": "Multiple transactions from same account exceeding $50,000 total within 24 hours",
  "category": "pattern_detection",
  "condition": {{
    "field": "amount",
    "operator": "greater_than",
    "value": 50000,
    "additional_conditions": [
      {{
        "field": "time_window",
        "operator": "less_than",
        "value": "24 hours"
      }},
      {{
        "field": "from_account",
        "operator": "equals",
        "value": "same_account"
      }}
    ],
    "logic": "AND"
  }},
  "severity": "critical",
  "page_reference": "Page 4, Section 2.2",
  "confidence_score": 0.95,
  "validation_query": "SELECT from_account, SUM(amount) FROM transactions WHERE timestamp > NOW() - INTERVAL '24 hours' GROUP BY from_account HAVING SUM(amount) > 50000"
}}

Example 3 - Type-Specific Limit:
{{
  "rule_id": "R003",
  "description": "Cash withdrawals exceeding $5,000 require manager approval",
  "category": "transaction_limit",
  "condition": {{
    "field": "amount",
    "operator": "greater_than",
    "value": 5000,
    "additional_conditions": [
      {{
        "field": "transaction_type",
        "operator": "equals",
        "value": "CASH_OUT"
      }}
    ],
    "logic": "AND"
  }},
  "severity": "medium",
  "page_reference": "Page 5, Section 3.1",
  "confidence_score": 0.97,
  "validation_query": "SELECT * FROM transactions WHERE transaction_type = 'CASH_OUT' AND amount > 5000"
}}

Now extract all rules from the provided policy document."""

    @staticmethod
    def validate_extracted_rules(rules: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """
        Validate that extracted rules have required fields and proper structure.
        
        Args:
            rules: List of extracted rule dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not rules:
            errors.append("No rules extracted")
            return False, errors
        
        required_fields = ["rule_id", "description", "category", "condition", "severity", "confidence_score"]
        valid_severities = ["critical", "high", "medium", "low"]
        valid_operators = [
            "greater_than", "less_than", "equals", "not_equals",
            "contains", "not_contains", "regex_match", "between"
        ]
        
        for idx, rule in enumerate(rules):
            rule_id = rule.get("rule_id", f"Rule {idx+1}")
            
            # Check required fields
            for field in required_fields:
                if field not in rule:
                    errors.append(f"{rule_id}: Missing required field '{field}'")
            
            # Validate severity
            if rule.get("severity") not in valid_severities:
                errors.append(f"{rule_id}: Invalid severity '{rule.get('severity')}'. Must be one of {valid_severities}")
            
            # Validate confidence score
            confidence = rule.get("confidence_score", 0)
            if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
                errors.append(f"{rule_id}: Confidence score must be between 0 and 1")
            
            # Validate condition structure
            condition = rule.get("condition", {})
            if not isinstance(condition, dict):
                errors.append(f"{rule_id}: Condition must be a dictionary")
                continue
            
            if "field" not in condition:
                errors.append(f"{rule_id}: Condition missing 'field'")
            
            if "operator" not in condition:
                errors.append(f"{rule_id}: Condition missing 'operator'")
            elif condition["operator"] not in valid_operators:
                errors.append(f"{rule_id}: Invalid operator '{condition['operator']}'")
            
            if "value" not in condition:
                errors.append(f"{rule_id}: Condition missing 'value'")
        
        return len(errors) == 0, errors
