"""Production-ready OpenAI prompt templates."""

from .rule_extraction import RuleExtractionPrompt
from .justification import JustificationPrompt
from .remediation import RemediationPrompt

__all__ = [
    "RuleExtractionPrompt",
    "JustificationPrompt",
    "RemediationPrompt",
]
