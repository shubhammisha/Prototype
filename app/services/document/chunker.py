from typing import List
from app.schemas.document import Document
import re

class DocumentChunker:
    """
    Splits large documents into overlapping chunks.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        chunked_docs = []
        
        for doc in documents:
            chunks = self._recursive_split_text(doc.text)
            
            for i, chunk_text in enumerate(chunks):
                # Create a new document object for each chunk
                # Preserve original metadata but add chunk index
                new_metadata = doc.metadata.copy()
                new_metadata["chunk_index"] = i
                
                chunked_docs.append(Document(
                    text=chunk_text,
                    metadata=new_metadata
                ))
        
        return chunked_docs

    def _recursive_split_text(self, text: str) -> List[str]:
        """
        Splits text trying to preserve semantic boundaries (paragraphs -> sentences -> chars).
        """
        if not text:
            return []
            
        if len(text) <= self.chunk_size:
            return [text]
            
        separators = ["\n\n", "\n", ". ", " "]
        
        for sep in separators:
            splits = text.split(sep)
            if len(splits) > 1:
                # Group splits back into chunks
                return self._merge_splits(splits, sep)
                
        # If no separators work (e.g. giant block of chars), hard split
        return self._hard_split(text)

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        docs = []
        current_doc = []
        total = 0
        
        for d in splits:
            _len = len(d)
            if total + _len + len(separator) > self.chunk_size:
                if total > self.chunk_size:
                    # Single chunk too big, split recursively
                    pass # Handled by outer logic if we were purely recursive, but simplistic here.
                    
                if current_doc:
                    doc = separator.join(current_doc)
                    if doc.strip():
                        docs.append(doc)
                    
                    # Overlap logic: Keep last few segments for context
                    # Rough overlap based on segment count? Or length.
                    # Implementing simple sliding window is cleaner but this is "recursive" style merge.
                    
                    # Reset with overlap
                    while total > self.chunk_overlap and current_doc:
                        removed = current_doc.pop(0)
                        total -= len(removed) + len(separator)
                    
                current_doc = [d]
                total = _len
            else:
                current_doc.append(d)
                total += _len + len(separator)
        
        if current_doc:
            doc = separator.join(current_doc)
            if doc.strip():
                docs.append(doc)
                
        return docs
        
    def _hard_split(self, text: str) -> List[str]:
        return [text[i:i+self.chunk_size] for i in range(0, len(text), self.chunk_size - self.chunk_overlap)]
