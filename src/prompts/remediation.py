"""Production-ready prompt templates for remediation suggestions."""

from typing import Dict, Any, List
from dataclasses import dataclass
import json


@dataclass
class RemediationPrompt:
    """Production prompt template for generating remediation suggestions."""
    
    SYSTEM_PROMPT = """You are a compliance consultant providing actionable remediation guidance.

Your recommendations should be:
- Specific and actionable (not vague advice)
- Prioritized by urgency and impact
- Practical and implementable
- Focused on preventing recurrence

Provide 2-4 concrete steps that can be taken immediately."""

    @staticmethod
    def build_remediation_prompt(
        rule_description: str,
        violation_justification: str,
        record_data: Dict[str, Any],
        severity: str
    ) -> str:
        """
        Build the user prompt for remediation suggestions.
        
        Args:
            rule_description: Description of the violated rule
            violation_justification: Why the violation occurred
            record_data: The violating record
            severity: Severity level of the violation
            
        Returns:
            Formatted prompt string
        """
        return f"""Generate specific, actionable remediation steps to resolve this compliance violation.

RULE VIOLATED:
{rule_description}

VIOLATION EXPLANATION:
{violation_justification}

RECORD DATA:
{json.dumps(record_data, indent=2)}

SEVERITY: {severity.upper()}

INSTRUCTIONS:
Provide 2-4 concrete remediation steps. Each step should:
- Be specific and actionable
- Include who should take the action (if relevant)
- Specify what needs to be done
- Be prioritized appropriately

Return as JSON:
{{
  "steps": [
    {{
      "step_number": 1,
      "action": "Specific action to take",
      "responsible_party": "Who should do this (e.g., Compliance Team, Account Manager, System Admin)",
      "priority": "immediate|high|medium|low",
      "estimated_time": "How long this will take (e.g., 1 hour, 1 day, 1 week)",
      "prevents_recurrence": true/false
    }}
  ],
  "additional_notes": "Any important context or warnings"
}}

EXAMPLES:

Example 1 - High-Value Transaction Violation:
Rule: Transactions over $10,000 must be flagged
Violation: Transaction of $15,750 was not flagged
Severity: High

Response:
{{
  "steps": [
    {{
      "step_number": 1,
      "action": "Immediately flag transaction TXN123456 for compliance review and document the reason for the delay in flagging",
      "responsible_party": "Compliance Team",
      "priority": "immediate",
      "estimated_time": "1 hour",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 2,
      "action": "Verify the source of funds and obtain supporting documentation from the account holder for this $15,750 transaction",
      "responsible_party": "Account Manager",
      "priority": "high",
      "estimated_time": "2 days",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 3,
      "action": "Review and update the automated flagging system to ensure all transactions above $10,000 are automatically flagged in real-time",
      "responsible_party": "System Admin",
      "priority": "high",
      "estimated_time": "1 week",
      "prevents_recurrence": true
    }},
    {{
      "step_number": 4,
      "action": "Conduct a retroactive scan of the past 30 days to identify any other high-value transactions that may have been missed",
      "responsible_party": "Compliance Team",
      "priority": "medium",
      "estimated_time": "3 days",
      "prevents_recurrence": false
    }}
  ],
  "additional_notes": "This violation indicates a potential gap in the automated monitoring system. Priority should be given to fixing the root cause to prevent future occurrences."
}}

Example 2 - Pattern Detection Violation:
Rule: No more than $50,000 total within 24 hours from same account
Violation: Account had $67,500 in 18 hours
Severity: Critical

Response:
{{
  "steps": [
    {{
      "step_number": 1,
      "action": "Immediately freeze account ACC0042 pending investigation and notify the account holder of the temporary restriction",
      "responsible_party": "Compliance Team",
      "priority": "immediate",
      "estimated_time": "30 minutes",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 2,
      "action": "Conduct enhanced due diligence on account ACC0042, including verification of business purpose for the rapid transaction pattern",
      "responsible_party": "AML Investigator",
      "priority": "immediate",
      "estimated_time": "1 day",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 3,
      "action": "File a Suspicious Activity Report (SAR) if the investigation reveals potential structuring or money laundering indicators",
      "responsible_party": "Compliance Officer",
      "priority": "high",
      "estimated_time": "2 days",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 4,
      "action": "Implement real-time alerts for accounts approaching the $50,000 threshold within 24 hours to enable proactive intervention",
      "responsible_party": "System Admin",
      "priority": "high",
      "estimated_time": "1 week",
      "prevents_recurrence": true
    }}
  ],
  "additional_notes": "Critical severity violations require immediate action and potential regulatory reporting. Document all investigation steps thoroughly for audit purposes."
}}

Example 3 - Cash Withdrawal Violation:
Rule: Cash withdrawals over $5,000 require manager approval
Violation: $7,200 withdrawal without approval
Severity: Medium

Response:
{{
  "steps": [
    {{
      "step_number": 1,
      "action": "Obtain retroactive manager approval for the $7,200 cash withdrawal and document the approval in the transaction record",
      "responsible_party": "Branch Manager",
      "priority": "high",
      "estimated_time": "4 hours",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 2,
      "action": "Contact the customer to verify the purpose of the cash withdrawal and document the business justification",
      "responsible_party": "Account Manager",
      "priority": "high",
      "estimated_time": "1 day",
      "prevents_recurrence": false
    }},
    {{
      "step_number": 3,
      "action": "Update the transaction processing system to require manager approval before completing cash withdrawals over $5,000",
      "responsible_party": "System Admin",
      "priority": "medium",
      "estimated_time": "1 week",
      "prevents_recurrence": true
    }}
  ],
  "additional_notes": "This appears to be a process gap rather than intentional circumvention. Focus on system controls to prevent future occurrences."
}}

Now generate remediation steps for the provided violation:"""

    @staticmethod
    def validate_remediation_steps(steps: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """
        Validate that remediation steps meet quality standards.
        
        Args:
            steps: List of remediation step dictionaries
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not steps or len(steps) == 0:
            errors.append("No remediation steps provided")
            return False, errors
        
        if len(steps) < 2:
            errors.append("Should provide at least 2 remediation steps")
        
        if len(steps) > 6:
            errors.append("Too many steps (maximum 6 for clarity)")
        
        required_fields = ["step_number", "action", "responsible_party", "priority", "estimated_time"]
        valid_priorities = ["immediate", "high", "medium", "low"]
        
        for idx, step in enumerate(steps):
            step_id = f"Step {idx+1}"
            
            # Check required fields
            for field in required_fields:
                if field not in step:
                    errors.append(f"{step_id}: Missing required field '{field}'")
            
            # Validate priority
            if step.get("priority") not in valid_priorities:
                errors.append(f"{step_id}: Invalid priority '{step.get('priority')}'. Must be one of {valid_priorities}")
            
            # Check action is specific enough
            action = step.get("action", "")
            if len(action.split()) < 5:
                errors.append(f"{step_id}: Action is too vague (less than 5 words)")
            
            # Check for vague language
            vague_terms = ["review", "consider", "maybe", "possibly", "might"]
            if any(term in action.lower() for term in vague_terms):
                errors.append(f"{step_id}: Action contains vague language - be more specific")
        
        # Check for at least one step that prevents recurrence
        has_prevention = any(step.get("prevents_recurrence", False) for step in steps)
        if not has_prevention:
            errors.append("Should include at least one step that prevents recurrence")
        
        return len(errors) == 0, errors
