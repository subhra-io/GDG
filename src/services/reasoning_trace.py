"""Reasoning trace generation service."""

import json
from typing import Dict, Any, List
from openai import OpenAI

from src.core.logging import get_logger
from src.config.settings import settings
from src.prompts.reasoning_trace import get_reasoning_trace_prompt

logger = get_logger(__name__)


class ReasoningTraceGenerator:
    """Generate step-by-step reasoning traces for violation decisions."""
    
    def __init__(self):
        """Initialize reasoning trace generator."""
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def generate_trace(
        self,
        rule_description: str,
        severity: str,
        record_data: Dict[str, Any],
        violation_details: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate a multi-step reasoning trace.
        
        Args:
            rule_description: Description of the compliance rule
            severity: Severity level
            record_data: The record being evaluated
            violation_details: Details about the violation
            
        Returns:
            List of reasoning steps
        """
        try:
            prompt = get_reasoning_trace_prompt(
                rule_description,
                severity,
                record_data,
                violation_details
            )
            
            logger.info("Generating reasoning trace")
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI compliance auditor that provides clear, step-by-step explanations of your reasoning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            try:
                steps = json.loads(content)
                
                # Validate and clean steps
                validated_steps = []
                for step in steps:
                    validated_step = {
                        "step_number": step.get("step_number", len(validated_steps) + 1),
                        "description": step.get("description", ""),
                        "rules_evaluated": step.get("rules_evaluated", []),
                        "policy_references": step.get("policy_references", []),
                        "confidence_score": min(100, max(0, step.get("confidence_score", 80))),
                        "outcome": step.get("outcome", "inconclusive")
                    }
                    validated_steps.append(validated_step)
                
                logger.info(
                    "Reasoning trace generated",
                    steps_count=len(validated_steps)
                )
                
                return validated_steps
                
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse reasoning trace JSON: {e}")
                # Return a default single-step trace
                return self._create_fallback_trace(
                    rule_description,
                    violation_details
                )
                
        except Exception as e:
            logger.error(f"Error generating reasoning trace: {e}")
            return self._create_fallback_trace(
                rule_description,
                violation_details
            )
    
    def _create_fallback_trace(
        self,
        rule_description: str,
        violation_details: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create a fallback reasoning trace when LLM fails.
        
        Args:
            rule_description: Rule description
            violation_details: Violation details
            
        Returns:
            Simple reasoning trace
        """
        return [
            {
                "step_number": 1,
                "description": f"Evaluated record against rule: {rule_description}",
                "rules_evaluated": [rule_description],
                "policy_references": [],
                "confidence_score": 75,
                "outcome": "fail"
            },
            {
                "step_number": 2,
                "description": f"Found violation: {violation_details.get('expected', 'Condition not met')}",
                "rules_evaluated": [rule_description],
                "policy_references": [],
                "confidence_score": 80,
                "outcome": "fail"
            }
        ]
    
    def format_trace_for_export(self, steps: List[Dict[str, Any]]) -> str:
        """
        Format trace as plain text for audit export.
        
        Args:
            steps: List of reasoning steps
            
        Returns:
            Formatted plain text
        """
        lines = ["REASONING TRACE", "=" * 50, ""]
        
        for step in steps:
            lines.append(f"Step {step['step_number']}: {step['description']}")
            lines.append(f"Confidence: {step['confidence_score']}%")
            lines.append(f"Outcome: {step['outcome']}")
            
            if step.get('rules_evaluated'):
                lines.append(f"Rules Evaluated: {', '.join(step['rules_evaluated'])}")
            
            if step.get('policy_references'):
                lines.append("Policy References:")
                for ref in step['policy_references']:
                    lines.append(f"  - {ref.get('clause', 'N/A')} (Page {ref.get('page', 'N/A')})")
            
            lines.append("")
        
        return "\n".join(lines)
