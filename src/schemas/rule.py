"""Rule schemas."""

from datetime import datetime
from typing import Dict, Any, List
from pydantic import BaseModel
from uuid import UUID


class ComplianceRuleResponse(BaseModel):
    """Compliance rule response."""
    id: UUID
    policy_document_id: UUID
    page_number: str | None
    description: str
    validation_logic: Dict[str, Any]
    severity: str
    is_active: bool
    confidence_score: str | None
    created_at: datetime
    
    class Config:
        from_attributes = True


class RuleExtractionResponse(BaseModel):
    """Response after rule extraction."""
    policy_id: UUID
    rules_extracted: int
    rules: List[ComplianceRuleResponse]
    status: str
    message: str
