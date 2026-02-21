"""PDF text extraction service."""

import hashlib
from pathlib import Path
from typing import Dict, Any
import pdfplumber

from src.core.logging import get_logger

logger = get_logger(__name__)


class PDFExtractionError(Exception):
    """PDF extraction error."""
    pass


class PDFExtractor:
    """Extract text from PDF documents."""
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(self):
        """Initialize PDF extractor."""
        pass
    
    def validate_pdf(self, file_path: Path) -> bool:
        """
        Validate PDF file.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            True if valid
            
        Raises:
            PDFExtractionError: If validation fails
        """
        if not file_path.exists():
            raise PDFExtractionError(f"File not found: {file_path}")
        
        file_size = file_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            raise PDFExtractionError(
                f"File size ({file_size} bytes) exceeds maximum ({self.MAX_FILE_SIZE} bytes)"
            )
        
        if not file_path.suffix.lower() == '.pdf':
            raise PDFExtractionError(f"File is not a PDF: {file_path}")
        
        return True
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        Calculate SHA-256 hash of file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex digest of file hash
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def extract_text(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract text from PDF with page numbers.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
            
        Raises:
            PDFExtractionError: If extraction fails
        """
        try:
            self.validate_pdf(file_path)
            
            logger.info("Extracting text from PDF", file=str(file_path))
            
            pages_text = []
            metadata = {
                "total_pages": 0,
                "has_tables": False
            }
            
            with pdfplumber.open(file_path) as pdf:
                metadata["total_pages"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, start=1):
                    # Extract text
                    text = page.extract_text()
                    if text:
                        pages_text.append({
                            "page_number": page_num,
                            "text": text.strip()
                        })
                    
                    # Check for tables
                    tables = page.extract_tables()
                    if tables:
                        metadata["has_tables"] = True
            
            if not pages_text:
                raise PDFExtractionError("No text could be extracted from PDF")
            
            # Combine all pages
            full_text = "\n\n".join([
                f"[Page {p['page_number']}]\n{p['text']}" 
                for p in pages_text
            ])
            
            logger.info(
                "PDF extraction successful",
                pages=metadata["total_pages"],
                text_length=len(full_text)
            )
            
            return {
                "text": full_text,
                "pages": pages_text,
                "metadata": metadata
            }
            
        except pdfplumber.PDFSyntaxError as e:
            logger.error("PDF syntax error", error=str(e))
            raise PDFExtractionError(f"Corrupted or invalid PDF: {str(e)}")
        except Exception as e:
            logger.error("PDF extraction failed", error=str(e))
            raise PDFExtractionError(f"Failed to extract text: {str(e)}")
