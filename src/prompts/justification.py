"""Production-ready prompt templates for violation justification."""

from typing import Dict, Any
from dataclasses import dataclass
import json


@dataclass
class JustificationPrompt:
    """Production prompt template for generating violation justifications."""
    
    SYSTEM_PROMPT = """You are a compliance officer explaining violations to business stakeholders.

Your explanations should be:
- Clear and concise (2-3 sentences maximum)
- Non-technical and business-friendly
- Specific about what was violated and why
- Factual without speculation

Focus on the gap between what the rule requires and what the record contains."""

    @staticmethod
    def build_justification_prompt(
        rule_description: str,
        rule_condition: Dict[str, Any],
        record_data: Dict[str, Any],
        violation_details: Dict[str, Any]
    ) -> str:
        """
        Build the user prompt for violation justification.
        
        Args:
            rule_description: Description of the violated rule
            rule_condition: The condition that was violated
            record_data: The record that violated the rule
            violation_details: Specific details about the violation
            
        Returns:
            Formatted prompt string
        """
        return f"""Explain why this record violates the compliance rule in clear, business-friendly language.

RULE DESCRIPTION:
{rule_description}

RULE REQUIREMENT:
{json.dumps(rule_condition, indent=2)}

RECORD DATA:
{json.dumps(record_data, indent=2)}

VIOLATION DETAILS:
{json.dumps(violation_details, indent=2)}

INSTRUCTIONS:
Generate a concise explanation (2-3 sentences) that:
1. States what the rule requires
2. Explains what the record contains
3. Clearly identifies the mismatch

Use business-friendly language. Avoid technical jargon.

EXAMPLES:

Example 1 - Amount Threshold:
Rule: Transactions exceeding $10,000 must be flagged
Record: Transaction amount is $15,750
Justification: "This transaction violates the high-value transaction policy, which requires flagging any single transaction exceeding $10,000. The transaction amount of $15,750 exceeds this threshold by $5,750, triggering a mandatory review requirement."

Example 2 - Pattern Violation:
Rule: No more than $50,000 in total transactions within 24 hours from same account
Record: Account ACC0042 had 5 transactions totaling $67,500 in 18 hours
Justification: "This account violated the suspicious pattern detection rule by conducting multiple transactions totaling $67,500 within an 18-hour period. The policy limit of $50,000 within 24 hours was exceeded by $17,500, which may indicate structuring activity."

Example 3 - Type-Specific Violation:
Rule: Cash withdrawals over $5,000 require manager approval
Record: CASH_OUT transaction of $7,200 without approval flag
Justification: "This cash withdrawal of $7,200 violates the cash transaction policy requiring manager approval for amounts exceeding $5,000. No approval documentation was found in the transaction record, making this a compliance violation."

Now generate the justification for the provided violation:"""

    @staticmethod
    def validate_justification(justification: str) -> tuple[bool, List[str]]:
        """
        Validate that the justification meets quality standards.
        
        Args:
            justification: The generated justification text
            
        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []
        
        if not justification or len(justification.strip()) == 0:
            return False, ["Justification is empty"]
        
        # Check length (should be concise)
        word_count = len(justification.split())
        if word_count < 10:
            warnings.append("Justification is too short (less than 10 words)")
        elif word_count > 150:
            warnings.append("Justification is too long (over 150 words)")
        
        # Check for technical jargon
        technical_terms = ["SQL", "database", "query", "schema", "API", "JSON"]
        found_jargon = [term for term in technical_terms if term in justification]
        if found_jargon:
            warnings.append(f"Contains technical jargon: {', '.join(found_jargon)}")
        
        # Check for key components
        if "violate" not in justification.lower() and "violation" not in justification.lower():
            warnings.append("Should explicitly mention 'violate' or 'violation'")
        
        # Should mention specific values
        if not any(char.isdigit() for char in justification):
            warnings.append("Should include specific numeric values from the violation")
        
        return len(warnings) == 0, warnings
