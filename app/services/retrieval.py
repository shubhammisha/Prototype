from typing import List
from app.services.vector.embeddings import BaseEmbeddingService, get_embedding_service
from app.services.vector.store import QdrantVectorStore
from app.schemas.vector import VectorEmbedding

class RetrievalService:
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.vector_store = QdrantVectorStore()
        
    def index_documents(self, texts: List[str], metadata_list: List[dict] | None = None):
        """
        Generate embeddings and index documents.
        """
        embeddings = self.embedding_service.embed_batch(texts, metadata_list)
        
        if embeddings:
            # Check dimension of first embedding to ensure collection exists with correct size
            dim = len(embeddings[0].vector)
            self.vector_store.ensure_collection(vector_size=dim)
            
            self.vector_store.upsert(embeddings)
            
    def search(self, query: str, limit: int = 5) -> List[VectorEmbedding]:
        """
        Search for relevant documents.
        """
        # 1. Embed query
        query_embedding_obj = self.embedding_service.embed_batch([query])[0]
        
        # 2. Search vector store
        results = self.vector_store.search(
            query_vector=query_embedding_obj.vector,
            limit=limit
        )
        
        return results
