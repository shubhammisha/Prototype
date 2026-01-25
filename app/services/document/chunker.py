import tiktoken

class DocumentChunker:
    """
    Splits text into chunks based on token count using tiktoken.
    """
    def __init__(self, model_name: str = "gpt-3.5-turbo"):
        try:
            self.encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            # Fallback to cl100k_base if model not found
            self.encoding = tiktoken.get_encoding("cl100k_base")

    def chunk(self, documents: list, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
        """
        Split documents into token-based chunks with overlap, preserving metadata.
        
        Args:
            documents: List of Document objects
            chunk_size: Maximum tokens per chunk
            chunk_overlap: Number of tokens to overlap between chunks
            
        Returns:
            List of Document objects (chunks)
        """
        if not documents:
            return []
            
        from app.schemas.document import Document # Import locally to avoid circular if any

        chunked_docs = []
        
        for doc in documents:
            text = doc.text
            meta = doc.metadata
            
            tokens = self.encoding.encode(text)
            total_tokens = len(tokens)
            
            if total_tokens <= chunk_size:
                chunked_docs.append(Document(text=text, metadata=meta))
                continue

            start = 0
            while start < total_tokens:
                end = start + chunk_size
                chunk_tokens = tokens[start:end]
                chunk_text = self.encoding.decode(chunk_tokens)
                
                # Create new document for chunk
                chunked_docs.append(Document(text=chunk_text, metadata=meta))
                
                if end >= total_tokens:
                    break
                    
                start += chunk_size - chunk_overlap
            
        return chunked_docs
