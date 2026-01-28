from typing import List, Optional, Union, Dict, Any
from app.services.vector.embeddings import BaseEmbeddingService, get_embedding_service
from app.services.vector.store import QdrantVectorStore
from app.services.vector.store import QdrantVectorStore
from app.schemas.vector import VectorEmbedding
from app.services.document.chunker import DocumentChunker
from app.schemas.document import Document

class RetrievalService:
    def __init__(self):
        import logging
        self.logger = logging.getLogger(__name__)
        self.embedding_service = get_embedding_service()
        self.embedding_service = get_embedding_service()
        self.vector_store = QdrantVectorStore()
        self.chunker = DocumentChunker()
        
    def index_documents(self, texts: List[str], metadata_list: Optional[List[dict]] = None):
        """
        Generate embeddings and index documents.
        """

        # 1. Chunk documents
        raw_docs = [
            Document(text=text, metadata=metadata_list[i] if metadata_list else {})
            for i, text in enumerate(texts)
        ]
        chunked_docs = self.chunker.chunk_documents(raw_docs)
        self.logger.info(f"Chunked {len(raw_docs)} documents into {len(chunked_docs)} chunks.")
        
        if not chunked_docs:
            return

        # 2. Embed chunks
        chunk_texts = [doc.text for doc in chunked_docs]
        chunk_metadatas = [doc.metadata for doc in chunked_docs]
        
        embeddings = self.embedding_service.embed_batch(chunk_texts, chunk_metadatas)
        
        if embeddings:
            # Check dimension of first embedding to ensure collection exists with correct size
            dim = len(embeddings[0].vector)
            self.vector_store.ensure_collection(vector_size=dim)
            
            self.vector_store.upsert(embeddings)
            
    def search(self, query: str, limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[VectorEmbedding]:
        """
        Search for relevant documents.
        """
        # 1. Embed query
        query_embedding_obj = self.embedding_service.embed_batch([query])[0]
        
        # 2. Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding_obj.vector,
            limit=limit,
            filters=filters
        )
        
        return results
