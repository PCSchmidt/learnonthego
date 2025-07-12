"""
PDF Processing Service for LearnOnTheGo
Extracts and processes text content from PDF documents for lecture generation
"""

import os
import re
from typing import Dict, Union
import pdfplumber
from io import BytesIO


class PDFService:
    """Service for extracting and processing PDF content"""
    
    def __init__(self):
        self.max_file_size = 50 * 1024 * 1024  # 50MB limit
        self.min_text_length = 100  # Minimum characters for valid PDF
        self.max_pages = 200  # Maximum pages to process
    
    async def extract_and_process(self, pdf_path: str) -> Dict[str, Union[str, bool]]:
        """
        Extract and process text content from PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dictionary with extracted content and metadata
        """
        try:
            # Validate file
            validation_result = self._validate_pdf_file(pdf_path)
            if not validation_result["valid"]:
                return {
                    "success": False,
                    "error": validation_result["error"]
                }
            
            # Extract text content
            extraction_result = self._extract_text_content(pdf_path)
            if not extraction_result["success"]:
                return extraction_result
            
            # Process and clean text
            processed_content = self._process_text_content(extraction_result["raw_text"])
            
            # Extract title from content or filename
            title = self._extract_title(processed_content, pdf_path)
            
            return {
                "success": True,
                "filename": os.path.basename(pdf_path),
                "extracted_title": title,
                "raw_text": extraction_result["raw_text"],
                "processed_content": processed_content,
                "page_count": extraction_result["page_count"],
                "word_count": len(processed_content.split()),
                "character_count": len(processed_content)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"PDF processing failed: {str(e)}"
            }
    
    def _validate_pdf_file(self, pdf_path: str) -> Dict[str, Union[str, bool]]:
        """Validate PDF file before processing"""
        try:
            # Check if file exists
            if not os.path.exists(pdf_path):
                return {"valid": False, "error": "PDF file not found"}
            
            # Check file size
            file_size = os.path.getsize(pdf_path)
            if file_size > self.max_file_size:
                return {
                    "valid": False, 
                    "error": f"PDF file too large ({file_size/1024/1024:.1f}MB). Maximum size is 50MB."
                }
            
            if file_size < 100:  # Very small file
                return {"valid": False, "error": "PDF file appears to be empty or corrupted"}
            
            # Try to open with pdfplumber to verify it's a valid PDF
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) == 0:
                    return {"valid": False, "error": "PDF has no pages"}
                
                if len(pdf.pages) > self.max_pages:
                    return {
                        "valid": False,
                        "error": f"PDF too long ({len(pdf.pages)} pages). Maximum is {self.max_pages} pages."
                    }
                
                # Quick text extraction test on first page
                first_page = pdf.pages[0]
                sample_text = first_page.extract_text() or ""
                
                if len(sample_text.strip()) < 10:
                    return {
                        "valid": False,
                        "error": "PDF appears to be scanned or image-based. Only text-based PDFs are supported."
                    }
            
            return {"valid": True}
            
        except Exception as e:
            return {"valid": False, "error": f"PDF validation failed: {str(e)}"}
    
    def _extract_text_content(self, pdf_path: str) -> Dict[str, Union[str, bool, int]]:
        """Extract raw text content from PDF"""
        try:
            extracted_text = ""
            page_count = 0
            
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_count += 1
                    
                    # Extract text from page
                    page_text = page.extract_text() or ""
                    
                    # Clean basic formatting issues
                    page_text = re.sub(r'\n+', '\n', page_text)  # Multiple newlines
                    page_text = re.sub(r' +', ' ', page_text)    # Multiple spaces
                    
                    extracted_text += page_text + "\n\n"
            
            # Validate extracted content
            if len(extracted_text.strip()) < self.min_text_length:
                return {
                    "success": False,
                    "error": "Insufficient text content extracted. PDF may be scanned or image-based."
                }
            
            return {
                "success": True,
                "raw_text": extracted_text.strip(),
                "page_count": page_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Text extraction failed: {str(e)}"
            }
    
    def _process_text_content(self, raw_text: str) -> str:
        """Clean and process extracted text for lecture generation"""
        
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', raw_text)
        text = re.sub(r' {2,}', ' ', text)
        
        # Remove page numbers and headers/footers (common patterns)
        text = re.sub(r'\n\d+\n', '\n', text)  # Standalone page numbers
        text = re.sub(r'\nPage \d+.*?\n', '\n', text, flags=re.IGNORECASE)
        
        # Clean up references and citations
        text = re.sub(r'\[\d+\]', '', text)  # Remove reference numbers
        text = re.sub(r'\([^)]*\d{4}[^)]*\)', '', text)  # Remove years in parentheses
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Clean up bullet points and formatting
        text = re.sub(r'^[•·\-\*]\s*', '', text, flags=re.MULTILINE)
        
        # Remove table-like structures (sequences of numbers/dots)
        text = re.sub(r'\n[.\s\d]+\n', '\n', text)
        
        # Final cleanup
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _extract_title(self, content: str, pdf_path: str) -> str:
        """Extract or generate a title for the lecture"""
        
        # Try to extract title from first few lines
        lines = content.split('\n')
        potential_titles = []
        
        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            line = line.strip()
            
            # Skip very short or very long lines
            if len(line) < 10 or len(line) > 100:
                continue
            
            # Skip lines that look like metadata
            if any(word in line.lower() for word in ['copyright', 'author', 'date', 'page', 'chapter']):
                continue
            
            # Look for title-like formatting
            if line.isupper() and len(line) > 15:  # All caps, reasonable length
                potential_titles.append(line.title())
            elif line.count('.') == 0 and len(line.split()) > 2:  # No periods, multiple words
                potential_titles.append(line.title())
        
        # Return best title candidate or fallback
        if potential_titles:
            return potential_titles[0][:80]  # Limit title length
        
        # Fallback to filename
        filename = os.path.basename(pdf_path)
        title = os.path.splitext(filename)[0]
        title = re.sub(r'[_-]', ' ', title)  # Replace underscores/hyphens with spaces
        
        return title.title()[:80]
    
    def validate_pdf_content(self, pdf_path: str) -> Dict[str, Union[str, bool]]:
        """Quick validation of PDF content without full processing"""
        try:
            validation = self._validate_pdf_file(pdf_path)
            if not validation["valid"]:
                return validation
            
            # Quick text sample
            with pdfplumber.open(pdf_path) as pdf:
                sample_text = ""
                for i, page in enumerate(pdf.pages[:3]):  # Check first 3 pages
                    page_text = page.extract_text() or ""
                    sample_text += page_text[:500]  # First 500 chars per page
                    if len(sample_text) > 1000:
                        break
            
            word_count = len(sample_text.split())
            
            return {
                "valid": True,
                "page_count": len(pdf.pages),
                "sample_word_count": word_count,
                "estimated_total_words": word_count * len(pdf.pages) // min(3, len(pdf.pages))
            }
            
        except Exception as e:
            return {"valid": False, "error": f"PDF validation failed: {str(e)}"}


# Service instance factory
def create_pdf_service() -> PDFService:
    """Create PDF service instance"""
    return PDFService()
