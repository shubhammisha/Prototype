import re
from typing import Union
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

class PDFLoader:
    """
    Service for loading and cleaning text from PDF files.
    """
    
    def load(self, file_path: Union[str, Path]) -> list:
        """
        Load a PDF file and return list of Documents with metadata.
        Tries to use PyMuPDF (fitz) for speed, falls back to pypdf.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"File {file_path} is not a PDF.")

        documents = []
        from app.schemas.document import Document

        # METHOD 1: Try PyMuPDF (Fast)
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(str(path))
            logger.info(f"Using PyMuPDF to load {path.name}")
            
            for i, page in enumerate(doc):
                try:
                    text = page.get_text()
                    if text:
                        cleaned_page_text = self._clean_text(text, page_num=i+1)
                        if cleaned_page_text:
                            documents.append(Document(
                                text=cleaned_page_text,
                                metadata={"page": i+1, "source": path.name}
                            ))
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {i+1} of {path.name}: {e}")
                    continue
            doc.close()
            return documents
            
        except ImportError:
            logger.warning("PyMuPDF (fitz) not found. Falling back to pypdf (slower).")
        except Exception as e:
            logger.error(f"PyMuPDF failed: {e}. Falling back to pypdf.")

        # METHOD 2: Fallback to pypdf (Slow but reliable if installed)
        try:
            from pypdf import PdfReader
            logger.info(f"Using pypdf to load {path.name}")
            reader = PdfReader(str(path))
            
            for i, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text:
                        cleaned_page_text = self._clean_text(text, page_num=i+1)
                        if cleaned_page_text:
                            documents.append(Document(
                                text=cleaned_page_text,
                                metadata={"page": i+1, "source": path.name}
                            ))
                except Exception as e:
                    logger.warning(f"Failed to extract text from page {i+1} of {path.name}: {e}")
                    continue
            return documents
            
        except Exception as e:
            logger.error(f"Error reading PDF {file_path} with pypdf: {e}")
            raise ValueError(f"Failed to read PDF: {e}. Ensure 'pymupdf' or 'pypdf' is installed.")

    def _clean_text(self, text: str, page_num: int = 0) -> str:
        """
        Apply heuristics to clean extracted text.
        
        Removes:
        - Excessive whitespace/newlines
        - Page numbers (simple heuristic)
        - Common headers/footers identifiers (if distinguishable)
        """
        # 1. Normalize whitespace (replace multiple spaces/tabs with single space)
        # Keeps newlines for now to distinguish paragraphs
        text = re.sub(r'[ \t]+', ' ', text)
        
        # 2. Remove multiple newlines (more than 2 becomes 2 to separate paragraphs)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 3. Split into lines for line-by-line processing
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Heuristic: Skip likely page numbers (e.g. "1", "Page 2", "- 3 -")
            if self._is_page_number(line, page_num):
                continue
                
            # Heuristic: Skip very short lines that might be headers/footers artifacts
            # (Be careful not to kill short titles or bullet points)
            if len(line) < 4 and not line[0].isalnum():
                 continue

            cleaned_lines.append(line)
            
        # Reassemble
        return "\n".join(cleaned_lines)

    def _is_page_number(self, line: str, page_num: int) -> bool:
        """
        Detect if a line is likely just a page number.
        """
        # Exact match digit or "Page X"
        if line.isdigit() and (int(line) == page_num or int(line) < 1000):
            return True
            
        # "Page X" or "pg X" case-insensitive
        if re.match(r'^(page|pg)\.?\s*\d+$', line, re.IGNORECASE):
            return True
        
        # "- X -" format
        if re.match(r'^-\s*\d+\s*-$', line):
            return True
            
        return False
