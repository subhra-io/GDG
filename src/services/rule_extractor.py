"""AI-powered rule extraction service using OpenAI."""

import json
from typing import List, Dict, Any
from openai import OpenAI

from src.config import settings
from src.core.logging import get_logger
from src.prompts import RuleExtractionPrompt, JustificationPrompt, RemediationPrompt

logger = get_logger(__name__)


class RuleExtractionError(Exception):
    """Rule extraction error."""
    pass


class RuleExtractor:
    """Extract compliance rules from policy text using LLM."""
    
    def __init__(self):
        """Initialize rule extractor."""
        if not settings.openai_api_key:
            logger.warning("OpenAI API key not configured")
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    def extract_rules(self, policy_text: str, policy_id: str) -> List[Dict[str, Any]]:
        """
        Extract compliance rules from policy text.
        
        Args:
            policy_text: Extracted policy text
            policy_id: Policy document ID
            
        Returns:
            List of extracted rules
            
        Raises:
            RuleExtractionError: If extraction fails
        """
        if not self.client:
            raise RuleExtractionError("OpenAI API key not configured")
        
        try:
            logger.info("Extracting rules using OpenAI", policy_id=policy_id)
            
            # Use production prompt template
            prompt = RuleExtractionPrompt.build_extraction_prompt(policy_text)
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": RuleExtractionPrompt.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            rules = result.get("rules", [])
            
            # Validate extracted rules
            is_valid, errors = RuleExtractionPrompt.validate_extracted_rules(rules)
            if not is_valid:
                logger.warning(
                    "Extracted rules have validation errors",
                    policy_id=policy_id,
                    errors=errors
                )
            
            logger.info(
                "Rules extracted successfully",
                policy_id=policy_id,
                rules_count=len(rules),
                validation_errors=len(errors) if not is_valid else 0
            )
            
            return rules
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse OpenAI response", error=str(e))
            raise RuleExtractionError(f"Invalid JSON response from OpenAI: {str(e)}")
        except Exception as e:
            logger.error("Rule extraction failed", error=str(e))
            raise RuleExtractionError(f"Failed to extract rules: {str(e)}")
    
    
    def generate_justification(
        self,
        rule_description: str,
        record_data: Dict[str, Any],
        violation_details: Dict[str, Any]
    ) -> str:
        """
        Generate human-readable justification for a violation.
        
        Args:
            rule_description: Description of the violated rule
            record_data: The record that violated the rule
            violation_details: Details about what was violated
            
        Returns:
            Natural language justification
        """
        if not self.client:
            return f"Violation detected: {rule_description}"
        
        try:
            # Use production prompt template
            rule_condition = violation_details.get("condition", {})
            prompt = JustificationPrompt.build_justification_prompt(
                rule_description,
                rule_condition,
                record_data,
                violation_details
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": JustificationPrompt.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            justification = response.choices[0].message.content.strip()
            
            # Validate justification quality
            is_valid, warnings = JustificationPrompt.validate_justification(justification)
            if not is_valid or warnings:
                logger.warning(
                    "Generated justification has quality issues",
                    warnings=warnings
                )
            
            return justification
            
        except Exception as e:
            logger.error("Failed to generate justification", error=str(e))
            return f"Violation detected: {rule_description}"
    
    def generate_remediation_steps(
        self,
        rule_description: str,
        violation_justification: str,
        record_data: Dict[str, Any],
        severity: str = "medium"
    ) -> List[Dict[str, str]]:
        """
        Generate remediation steps for a violation.
        
        Args:
            rule_description: Description of the violated rule
            violation_justification: Why the violation occurred
            record_data: The violating record
            severity: Severity level of the violation
            
        Returns:
            List of remediation steps
        """
        if not self.client:
            return [{"step": "Review and correct the violation", "priority": "high"}]
        
        try:
            # Use production prompt template
            prompt = RemediationPrompt.build_remediation_prompt(
                rule_description,
                violation_justification,
                record_data,
                severity
            )
            
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": RemediationPrompt.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            steps = result.get("steps", [])
            
            # Validate remediation steps
            is_valid, errors = RemediationPrompt.validate_remediation_steps(steps)
            if not is_valid:
                logger.warning(
                    "Generated remediation steps have validation errors",
                    errors=errors
                )
            
            return steps
            
        except Exception as e:
            logger.error("Failed to generate remediation steps", error=str(e))
            return [{"step": "Review and correct the violation", "priority": "high"}]
