"""Prompts for generating reasoning traces."""

REASONING_TRACE_PROMPT = """You are an AI compliance auditor explaining your decision-making process.

Given a compliance violation, generate a step-by-step reasoning trace that shows how you reached the conclusion that this is a violation.

VIOLATION CONTEXT:
Rule Description: {rule_description}
Rule Severity: {severity}
Record Data: {record_data}
Violation Details: {violation_details}

Generate a reasoning trace with 3-5 steps that:
1. Explains what you evaluated first
2. Shows the logic applied at each step
3. References specific policy requirements
4. Includes confidence scores (0-100) for each step
5. Shows the final conclusion

Format your response as a JSON array of reasoning steps:
[
  {{
    "step_number": 1,
    "description": "Clear explanation of what was evaluated",
    "rules_evaluated": ["rule name or ID"],
    "policy_references": [
      {{
        "clause": "Specific policy clause text",
        "page": 1,
        "document_name": "Policy document name"
      }}
    ],
    "confidence_score": 95,
    "outcome": "pass" or "fail" or "inconclusive"
  }},
  ...
]

Be specific, clear, and provide actionable insights. Each step should build on the previous one to show your reasoning chain.
"""


def get_reasoning_trace_prompt(
    rule_description: str,
    severity: str,
    record_data: dict,
    violation_details: dict
) -> str:
    """
    Get the reasoning trace generation prompt.
    
    Args:
        rule_description: Description of the compliance rule
        severity: Severity level of the violation
        record_data: The record that violated the rule
        violation_details: Details about the violation
        
    Returns:
        Formatted prompt string
    """
    return REASONING_TRACE_PROMPT.format(
        rule_description=rule_description,
        severity=severity,
        record_data=str(record_data),
        violation_details=str(violation_details)
    )
