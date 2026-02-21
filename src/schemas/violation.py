"""Violation schemas."""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from uuid import UUID


class ViolationResponse(BaseModel):
    """Violation response."""
    id: UUID
    rule_id: UUID
    record_identifier: str
    table_name: str
    detected_at: datetime
    status: str
    severity: str
    justification: str
    
    class Config:
        from_attributes = True


class ViolationDetailResponse(BaseModel):
    """Detailed violation response."""
    id: UUID
    rule_id: UUID
    record_identifier: str
    table_name: str
    detected_at: datetime
    status: str
    severity: str
    justification: str
    record_snapshot: Dict[str, Any]
    remediation_steps: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True
