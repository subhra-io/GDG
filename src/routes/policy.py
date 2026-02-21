"""Policy management routes."""

import tempfile
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.core.database import db_manager
from src.core.logging import get_logger
from src.models import PolicyDocument, ComplianceRule
from src.schemas import (
    PolicyDocumentResponse,
    PolicyUploadResponse,
    ComplianceRuleResponse,
    RuleExtractionResponse
)
from src.services import PDFExtractor, RuleExtractor
from src.models.policy import PolicyStatus
from src.models.rule import Severity

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/policies", tags=["policies"])


def get_db():
    """Get database session."""
    session = db_manager.get_postgres_session()
    try:
        yield session
    finally:
        session.close()


@router.post("/upload", response_model=PolicyUploadResponse)
async def upload_policy(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a policy PDF document.
    
    Args:
        file: PDF file to upload
        db: Database session
        
    Returns:
        Upload response with policy ID
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = Path(tmp_file.name)
        
        try:
            # Extract text from PDF
            pdf_extractor = PDFExtractor()
            file_hash = pdf_extractor.calculate_file_hash(tmp_path)
            
            # Check for duplicate
            existing = db.query(PolicyDocument).filter(
                PolicyDocument.file_hash == file_hash
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"Policy document already exists with ID: {existing.id}"
                )
            
            extraction_result = pdf_extractor.extract_text(tmp_path)
            
            # Create policy document record
            policy = PolicyDocument(
                filename=file.filename,
                file_size_bytes=tmp_path.stat().st_size,
                file_hash=file_hash,
                status=PolicyStatus.PROCESSED,
                extracted_text=extraction_result["text"],
                metadata=extraction_result["metadata"]
            )
            
            db.add(policy)
            db.commit()
            db.refresh(policy)
            
            logger.info(
                "Policy uploaded successfully",
                policy_id=str(policy.id),
                filename=file.filename
            )
            
            return PolicyUploadResponse(
                policy_id=policy.id,
                filename=policy.filename,
                status=policy.status.value,
                message="Policy uploaded and processed successfully"
            )
            
        finally:
            # Clean up temporary file
            tmp_path.unlink(missing_ok=True)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Policy upload failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/{policy_id}/extract-rules", response_model=RuleExtractionResponse)
async def extract_rules(
    policy_id: str,
    db: Session = Depends(get_db)
):
    """
    Extract compliance rules from a policy document using AI.
    
    Args:
        policy_id: Policy document ID
        db: Database session
        
    Returns:
        Extracted rules
    """
    try:
        # Get policy document
        policy = db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        if not policy.extracted_text:
            raise HTTPException(
                status_code=400,
                detail="Policy has no extracted text"
            )
        
        # Extract rules using AI
        rule_extractor = RuleExtractor()
        extracted_rules = rule_extractor.extract_rules(
            policy.extracted_text,
            str(policy.id)
        )
        
        # Save rules to database
        saved_rules = []
        for rule_data in extracted_rules:
            rule = ComplianceRule(
                policy_document_id=policy.id,
                page_number=rule_data.get("page_number"),
                description=rule_data.get("description", ""),
                validation_logic=rule_data.get("condition", {}),
                severity=Severity(rule_data.get("severity", "medium").lower()),
                confidence_score=str(rule_data.get("confidence_score", 0.0)),
                is_active=True
            )
            db.add(rule)
            saved_rules.append(rule)
        
        db.commit()
        
        # Refresh to get IDs
        for rule in saved_rules:
            db.refresh(rule)
        
        logger.info(
            "Rules extracted successfully",
            policy_id=policy_id,
            rules_count=len(saved_rules)
        )
        
        return RuleExtractionResponse(
            policy_id=policy.id,
            rules_extracted=len(saved_rules),
            rules=[ComplianceRuleResponse.model_validate(r) for r in saved_rules],
            status="success",
            message=f"Extracted {len(saved_rules)} rules successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Rule extraction failed", error=str(e), policy_id=policy_id)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")


@router.get("", response_model=List[PolicyDocumentResponse])
async def list_policies(db: Session = Depends(get_db)):
    """
    List all policy documents.
    
    Args:
        db: Database session
        
    Returns:
        List of policies
    """
    policies = db.query(PolicyDocument).order_by(
        PolicyDocument.upload_timestamp.desc()
    ).all()
    
    # Enrich with rules count and policy type
    result = []
    for policy in policies:
        # Count rules
        rules_count = db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy.id
        ).count()
        
        # Extract policy type from metadata or filename
        policy_type = None
        if policy.document_metadata:
            policy_type = policy.document_metadata.get('policy_type')
        if not policy_type and policy.filename:
            filename_upper = policy.filename.upper()
            if 'AML' in filename_upper:
                policy_type = 'AML'
            elif 'GDPR' in filename_upper:
                policy_type = 'GDPR'
            elif 'SOX' in filename_upper:
                policy_type = 'SOX'
            elif 'HIPAA' in filename_upper:
                policy_type = 'HIPAA'
            elif 'PCI' in filename_upper:
                policy_type = 'PCI-DSS'
        
        # Create response with additional fields
        policy_dict = {
            'id': policy.id,
            'filename': policy.filename,
            'upload_timestamp': policy.upload_timestamp,
            'uploaded_at': policy.upload_timestamp,
            'file_size_bytes': policy.file_size_bytes,
            'file_size': policy.file_size_bytes,
            'status': policy.status.value,
            'extracted_text': policy.extracted_text,
            'document_metadata': policy.document_metadata,
            'error_message': policy.error_message,
            'policy_type': policy_type,
            'rules_count': rules_count
        }
        result.append(PolicyDocumentResponse(**policy_dict))
    
    return result


@router.get("/{policy_id}", response_model=PolicyDocumentResponse)
async def get_policy(policy_id: str, db: Session = Depends(get_db)):
    """
    Get a specific policy document.
    
    Args:
        policy_id: Policy document ID
        db: Database session
        
    Returns:
        Policy document
    """
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    return PolicyDocumentResponse.model_validate(policy)


@router.get("/{policy_id}/rules", response_model=List[ComplianceRuleResponse])
async def get_policy_rules(policy_id: str, db: Session = Depends(get_db)):
    """
    Get all rules for a policy document.
    
    Args:
        policy_id: Policy document ID
        db: Database session
        
    Returns:
        List of rules
    """
    rules = db.query(ComplianceRule).filter(
        ComplianceRule.policy_document_id == policy_id
    ).all()
    
    return [ComplianceRuleResponse.model_validate(r) for r in rules]


@router.delete("/{policy_id}")
async def delete_policy(policy_id: str, db: Session = Depends(get_db)):
    """
    Delete a policy document and all associated rules.
    
    Args:
        policy_id: Policy document ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        # Get policy
        policy = db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Delete associated rules first
        db.query(ComplianceRule).filter(
            ComplianceRule.policy_document_id == policy_id
        ).delete()
        
        # Delete policy
        db.delete(policy)
        db.commit()
        
        logger.info("Policy deleted successfully", policy_id=policy_id)
        
        return {
            "status": "success",
            "message": f"Policy {policy_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Policy deletion failed", error=str(e), policy_id=policy_id)
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.put("/{policy_id}")
async def update_policy(
    policy_id: str,
    filename: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Update policy document metadata.
    
    Args:
        policy_id: Policy document ID
        filename: New filename (optional)
        db: Database session
        
    Returns:
        Updated policy
    """
    try:
        # Get policy
        policy = db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if not policy:
            raise HTTPException(status_code=404, detail="Policy not found")
        
        # Update fields
        if filename:
            policy.filename = filename
        
        db.commit()
        db.refresh(policy)
        
        logger.info("Policy updated successfully", policy_id=policy_id)
        
        return PolicyDocumentResponse.model_validate(policy)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Policy update failed", error=str(e), policy_id=policy_id)
        raise HTTPException(status_code=500, detail=f"Update failed: {str(e)}")
