# 🚀 Day 4 Guide: Enhanced Reasoning Traces

## 🎯 Goal
Improve the reasoning trace feature with policy clause references, page numbers, and better UI integration.

---

## 📋 Tasks for Day 4

### Morning (3 hours): Backend Enhancements

#### 1. Update Reasoning Trace Prompt
**File**: `src/prompts/reasoning_trace.py`

Add clause reference extraction:
```python
# Add to the prompt
"""
For each reasoning step, include:
1. The specific policy clause being referenced
2. The page number where the clause appears
3. The section number (if available)
4. The exact clause text (quoted)

Example format:
{
    "step": 1,
    "description": "Checking transaction amount threshold",
    "clause_reference": {
        "text": "All transactions above $10,000 must be reported",
        "page": 5,
        "section": "2.3.1",
        "document": "AML Policy v2.1"
    },
    "confidence": 0.95
}
"""
```

#### 2. Add Page Number Extraction
**File**: `src/services/pdf_extractor.py`

Add method to extract page numbers:
```python
def extract_with_page_numbers(self, pdf_path: str) -> List[Dict[str, Any]]:
    """Extract text with page numbers."""
    pages = []
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            text = page.extract_text()
            pages.append({
                "page_number": page_num,
                "text": text,
                "char_count": len(text)
            })
    return pages
```

#### 3. Create Clause Highlighting Service
**File**: `src/services/clause_highlighter.py`

```python
"""Service for highlighting policy clauses."""

from typing import Dict, Any, List
from sqlalchemy.orm import Session
from src.models.policy_document import PolicyDocument
from src.services.pdf_extractor import PDFExtractor

class ClauseHighlighter:
    """Highlight specific clauses in policy documents."""
    
    def __init__(self, db: Session):
        self.db = db
        self.pdf_extractor = PDFExtractor()
    
    def find_clause_location(
        self,
        policy_id: str,
        clause_text: str
    ) -> Dict[str, Any]:
        """
        Find the location of a clause in a policy document.
        
        Args:
            policy_id: Policy document ID
            clause_text: Text to search for
            
        Returns:
            Location information with page number and position
        """
        policy = self.db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if not policy or not policy.file_path:
            return None
        
        # Extract pages with numbers
        pages = self.pdf_extractor.extract_with_page_numbers(policy.file_path)
        
        # Search for clause
        for page in pages:
            if clause_text.lower() in page['text'].lower():
                # Find position in text
                position = page['text'].lower().find(clause_text.lower())
                
                # Get surrounding context
                start = max(0, position - 100)
                end = min(len(page['text']), position + len(clause_text) + 100)
                context = page['text'][start:end]
                
                return {
                    "page_number": page['page_number'],
                    "position": position,
                    "context": context,
                    "found": True
                }
        
        return {"found": False}
    
    def get_clause_with_context(
        self,
        policy_id: str,
        page_number: int,
        section: str = None
    ) -> Dict[str, Any]:
        """Get clause text with surrounding context."""
        policy = self.db.query(PolicyDocument).filter(
            PolicyDocument.id == policy_id
        ).first()
        
        if not policy or not policy.file_path:
            return None
        
        pages = self.pdf_extractor.extract_with_page_numbers(policy.file_path)
        
        if page_number <= len(pages):
            page = pages[page_number - 1]
            return {
                "page_number": page_number,
                "text": page['text'],
                "section": section
            }
        
        return None
```

#### 4. Update Reasoning Trace Service
**File**: `src/services/reasoning_trace.py`

Update to include clause references:
```python
# Add to generate_reasoning_trace method
# After getting the trace from LLM, enhance it with clause locations

for step in trace_data.get('steps', []):
    if 'clause_reference' in step:
        clause_ref = step['clause_reference']
        
        # Find clause location
        highlighter = ClauseHighlighter(self.db)
        location = highlighter.find_clause_location(
            policy_id=violation.policy_document_id,
            clause_text=clause_ref.get('text', '')
        )
        
        if location and location.get('found'):
            step['clause_reference']['location'] = location
```

---

### Afternoon (3 hours): Frontend Enhancements

#### 5. Update ReasoningTraceViewer Component
**File**: `frontend/components/ReasoningTraceViewer.tsx`

Add clause reference display:
```typescript
// Add to each step display
{step.clause_reference && (
  <div className="mt-2 bg-blue-50 border border-blue-200 rounded p-2">
    <div className="text-xs font-semibold text-blue-900 mb-1">
      📄 Policy Reference
    </div>
    <div className="text-xs text-blue-800">
      <p className="font-medium">{step.clause_reference.document}</p>
      <p>Section {step.clause_reference.section} | Page {step.clause_reference.page}</p>
      <p className="mt-1 italic">"{step.clause_reference.text}"</p>
    </div>
    {step.clause_reference.location && (
      <button
        onClick={() => viewClause(step.clause_reference)}
        className="mt-2 text-xs text-blue-600 hover:text-blue-800 underline"
      >
        View in Policy Document →
      </button>
    )}
  </div>
)}
```

#### 6. Add Export to PDF Functionality
**File**: `frontend/components/ReasoningTraceViewer.tsx`

```typescript
import jsPDF from 'jspdf';

const exportToPdf = () => {
  const doc = new jsPDF();
  
  // Add title
  doc.setFontSize(16);
  doc.text('Reasoning Trace Report', 20, 20);
  
  // Add violation info
  doc.setFontSize(12);
  doc.text(`Violation ID: ${violationId}`, 20, 35);
  doc.text(`Generated: ${new Date().toLocaleString()}`, 20, 45);
  
  // Add steps
  let yPos = 60;
  trace.steps.forEach((step, idx) => {
    doc.setFontSize(11);
    doc.text(`Step ${idx + 1}: ${step.description}`, 20, yPos);
    yPos += 10;
    
    if (step.clause_reference) {
      doc.setFontSize(9);
      doc.text(`Reference: ${step.clause_reference.text}`, 25, yPos);
      yPos += 7;
      doc.text(`Page ${step.clause_reference.page}, Section ${step.clause_reference.section}`, 25, yPos);
      yPos += 10;
    }
    
    yPos += 5;
    
    // Add new page if needed
    if (yPos > 270) {
      doc.addPage();
      yPos = 20;
    }
  });
  
  // Save
  doc.save(`reasoning-trace-${violationId}.pdf`);
};
```

#### 7. Add Clause Viewer Modal
**File**: `frontend/components/ClauseViewer.tsx`

```typescript
'use client';

import { useState } from 'react';

interface ClauseViewerProps {
  policyId: string;
  pageNumber: number;
  clauseText: string;
  onClose: () => void;
}

export default function ClauseViewer({
  policyId,
  pageNumber,
  clauseText,
  onClose
}: ClauseViewerProps) {
  const [loading, setLoading] = useState(true);
  const [pageText, setPageText] = useState('');

  useEffect(() => {
    fetchPageText();
  }, [policyId, pageNumber]);

  const fetchPageText = async () => {
    try {
      const response = await fetch(
        `http://localhost:8000/api/v1/policies/${policyId}/page/${pageNumber}`
      );
      const data = await response.json();
      setPageText(data.text);
    } catch (err) {
      console.error('Failed to fetch page:', err);
    } finally {
      setLoading(false);
    }
  };

  const highlightClause = (text: string) => {
    const index = text.toLowerCase().indexOf(clauseText.toLowerCase());
    if (index === -1) return text;

    return (
      <>
        {text.substring(0, index)}
        <mark className="bg-yellow-200">{text.substring(index, index + clauseText.length)}</mark>
        {text.substring(index + clauseText.length)}
      </>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[80vh] overflow-hidden">
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="text-lg font-semibold">Policy Document - Page {pageNumber}</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ✕
          </button>
        </div>
        
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {loading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading page...</p>
            </div>
          ) : (
            <div className="prose max-w-none">
              <pre className="whitespace-pre-wrap font-sans text-sm">
                {highlightClause(pageText)}
              </pre>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

### Evening (2 hours): API Endpoints & Testing

#### 8. Add Policy Page Endpoint
**File**: `src/routes/policy.py`

```python
@router.get("/{policy_id}/page/{page_number}")
def get_policy_page(
    policy_id: str,
    page_number: int,
    db: Session = Depends(get_db)
):
    """Get specific page from policy document."""
    policy = db.query(PolicyDocument).filter(
        PolicyDocument.id == policy_id
    ).first()
    
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    
    if not policy.file_path:
        raise HTTPException(status_code=400, detail="Policy file not found")
    
    extractor = PDFExtractor()
    pages = extractor.extract_with_page_numbers(policy.file_path)
    
    if page_number < 1 or page_number > len(pages):
        raise HTTPException(status_code=404, detail="Page not found")
    
    return pages[page_number - 1]
```

#### 9. Add Clause Search Endpoint
**File**: `src/routes/policy.py`

```python
@router.post("/{policy_id}/search-clause")
def search_clause(
    policy_id: str,
    clause_text: str,
    db: Session = Depends(get_db)
):
    """Search for a clause in policy document."""
    highlighter = ClauseHighlighter(db)
    location = highlighter.find_clause_location(policy_id, clause_text)
    return location
```

#### 10. Test with Valid API Key
```bash
# Update .env with valid OpenAI key
OPENAI_API_KEY=sk-...

# Restart backend
# Test reasoning trace generation
curl -X POST http://localhost:8000/api/v1/violations/{id}/reasoning-trace

# Verify clause references are included
# Check page numbers are correct
# Test export to PDF
```

---

## ✅ Day 4 Checklist

- [ ] Update reasoning trace prompt with clause references
- [ ] Add page number extraction to PDF extractor
- [ ] Create clause highlighter service
- [ ] Update reasoning trace service
- [ ] Enhance ReasoningTraceViewer component
- [ ] Add export to PDF functionality
- [ ] Create clause viewer modal
- [ ] Add policy page endpoint
- [ ] Add clause search endpoint
- [ ] Test with valid API key
- [ ] Verify all features work together

---

## 🧪 Testing Day 4 Work

```bash
# Test page extraction
curl http://localhost:8000/api/v1/policies/{id}/page/1

# Test clause search
curl -X POST http://localhost:8000/api/v1/policies/{id}/search-clause \
  -H "Content-Type: application/json" \
  -d '{"clause_text": "transaction amount"}'

# Test reasoning trace with references
curl -X POST http://localhost:8000/api/v1/violations/{id}/reasoning-trace

# Test frontend
open http://localhost:3003/violations/{id}
# Click "View Reasoning Trace"
# Verify clause references appear
# Click "View in Policy Document"
# Click "Export to PDF"
```

---

## 💡 Tips for Success

1. **Start with backend** - Get data flowing first
2. **Test incrementally** - Don't wait until the end
3. **Use valid API key** - Essential for testing
4. **Check page numbers** - Verify they match PDF
5. **Test export** - Ensure PDF looks professional

---

## 🚀 Expected Outcome

By end of Day 4, you'll have:
- ✅ Reasoning traces with policy clause references
- ✅ Page numbers and section numbers
- ✅ Clickable links to view clauses
- ✅ Clause highlighting in policy viewer
- ✅ Export to PDF with references
- ✅ Professional, production-ready feature

---

**Let's make reasoning traces even better! 💪**
