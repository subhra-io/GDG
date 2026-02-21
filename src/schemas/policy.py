"""Policy schemas."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class PolicyDocumentResponse(BaseModel):
    """Policy document response."""
    id: UUID
    filename: str
    upload_timestamp: datetime
    uploaded_at: datetime = Field(alias="upload_timestamp")  # Alias for frontend
    file_size_bytes: int
    file_size: int = Field(alias="file_size_bytes")  # Alias for frontend
    status: str
    extracted_text: Optional[str] = None
    document_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")
    error_message: Optional[str] = None
    policy_type: Optional[str] = None  # Extracted from metadata or filename
    rules_count: int = 0  # Count of associated rules
    
    class Config:
        from_attributes = True
        populate_by_name = True


class PolicyUploadResponse(BaseModel):
    """Response after policy upload."""
    policy_id: UUID
    filename: str
    status: str
    message: str
