"""Service for highlighting and locating policy clauses."""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.models.policy_document import PolicyDocument
from src.services.pdf_extractor import PDFExtractor
from src.core.logging import get_logger

logger = get_logger(__name__)


class ClauseHighlighter:
    """Highlight and locate specific clauses in policy documents."""
    
    def __init__(self, db: Session):
        """
        Initialize clause highlighter.
        
        Args:
            db: Database session
        """
        self.db = db
        self.pdf_extractor = PDFExtractor()
    
    def find_clause_location(
        self,
        policy_id: str,
        clause_text: str,
        context_chars: int = 200
    ) -> Optional[Dict[str, Any]]:
        """
        Find the location of a clause in a policy document.
        
        Args:
            policy_id: Policy document ID
            clause_text: Text to search for
            context_chars: Number of characters to include as context
            
        Returns:
            Location information with page number and context, or None if not found
        """
        try:
            # Get policy document
            policy = self.db.query(PolicyDocument).filter(
                PolicyDocument.id == policy_id
            ).first()
            
            if not policy:
                logger.warning("Policy not found", policy_id=policy_id)
                return None
            
            if not policy.file_path:
                logger.warning("Policy has no file path", policy_id=policy_id)
                return None
            
            # Extract text with page numbers
            extraction_result = self.pdf_extractor.extract_text(policy.file_path)
            pages = extraction_result.get("pages", [])
            
            # Search for clause in pages
            clause_lower = clause_text.lower().strip()
            
            for page in pages:
                page_text = page["text"]
                page_text_lower = page_text.lower()
                
                # Find clause in page
                position = page_text_lower.find(clause_lower)
                
                if position != -1:
                    # Extract context around the clause
                    start = max(0, position - context_chars)
                    end = min(len(page_text), position + len(clause_text) + context_chars)
                    context = page_text[start:end]
                    
                    # Add ellipsis if truncated
                    if start > 0:
                        context = "..." + context
                    if end < len(page_text):
                        context = context + "..."
                    
                    logger.info(
                        "Clause found",
                        policy_id=policy_id,
                        page=page["page_number"],
                        position=position
                    )
                    
                    return {
                        "found": True,
                        "page_number": page["page_number"],
                        "position": position,
                        "context": context,
                        "clause_text": clause_text,
                        "page_text_length": len(page_text)
                    }
            
            logger.info("Clause not found", policy_id=policy_id, clause=clause_text[:50])
            return {"found": False, "clause_text": clause_text}
            
        except Exception as e:
            logger.error("Error finding clause", error=str(e), policy_id=policy_id)
            return {"found": False, "error": str(e)}
    
    def get_page_text(
        self,
        policy_id: str,
        page_number: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get text from a specific page of a policy document.
        
        Args:
            policy_id: Policy document ID
            page_number: Page number (1-indexed)
            
        Returns:
            Page text and metadata, or None if not found
        """
        try:
            # Get policy document
            policy = self.db.query(PolicyDocument).filter(
                PolicyDocument.id == policy_id
            ).first()
            
            if not policy or not policy.file_path:
                return None
            
            # Extract text with page numbers
            extraction_result = self.pdf_extractor.extract_text(policy.file_path)
            pages = extraction_result.get("pages", [])
            
            # Find the requested page
            for page in pages:
                if page["page_number"] == page_number:
                    return {
                        "page_number": page_number,
                        "text": page["text"],
                        "total_pages": extraction_result["metadata"]["total_pages"]
                    }
            
            logger.warning(
                "Page not found",
                policy_id=policy_id,
                page_number=page_number,
                total_pages=len(pages)
            )
            return None
            
        except Exception as e:
            logger.error("Error getting page text", error=str(e), policy_id=policy_id)
            return None
    
    def search_clauses(
        self,
        policy_id: str,
        search_terms: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Search for multiple clauses in a policy document.
        
        Args:
            policy_id: Policy document ID
            search_terms: List of terms to search for
            
        Returns:
            List of found clauses with locations
        """
        results = []
        
        for term in search_terms:
            location = self.find_clause_location(policy_id, term)
            if location and location.get("found"):
                results.append(location)
        
        return results
    
    def highlight_clause_in_text(
        self,
        text: str,
        clause_text: str,
        highlight_tag: str = "mark"
    ) -> str:
        """
        Add HTML highlighting to a clause in text.
        
        Args:
            text: Full text
            clause_text: Clause to highlight
            highlight_tag: HTML tag to use for highlighting
            
        Returns:
            Text with highlighted clause
        """
        # Case-insensitive search
        text_lower = text.lower()
        clause_lower = clause_text.lower()
        
        position = text_lower.find(clause_lower)
        
        if position == -1:
            return text
        
        # Extract the actual text (preserving case)
        actual_clause = text[position:position + len(clause_text)]
        
        # Add highlighting
        highlighted = f"<{highlight_tag}>{actual_clause}</{highlight_tag}>"
        
        # Replace in original text
        result = text[:position] + highlighted + text[position + len(clause_text):]
        
        return result
