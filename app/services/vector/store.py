from typing import List
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.core.config import settings
from app.schemas.vector import VectorEmbedding
import logging

logger = logging.getLogger(__name__)

# Global client instance for local mode concurrency handling
_client_instance = None

class QdrantVectorStore:
    def __init__(self):
        global _client_instance
        
        if _client_instance:
            self.client = _client_instance
        else:
            url = str(settings.VECTOR_DB_URL)
            if url.startswith("http"):
                self.client = QdrantClient(url=url, api_key=settings.VECTOR_DB_API_KEY)
            else:
                self.client = QdrantClient(path=url)
            
            # Cache the instance
            _client_instance = self.client
        
        self.collection_name = settings.VECTOR_COLLECTION_NAME


    def ensure_collection(self, vector_size: int = 768):
        """
        Create collection if it doesn't exist.
        Default 768 is for nomic-embed-text-v1.5.
        """
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection {self.collection_name} with size {vector_size}")

    def upsert(self, embeddings: List[VectorEmbedding]):
        if not embeddings:
            return

        points = []
        for i, emb in enumerate(embeddings):
            # Using simple auto-id or hash of text could be better
            # For now, let's assume UUIDs are generated or use simple index if not provided
            # Better: Use uuid5 of text to ensure idempotency
            import uuid
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, emb.text))
            
            points.append(models.PointStruct(
                id=point_id,
                vector=emb.vector,
                payload={
                    "text": emb.text,
                    **emb.metadata
                }
            ))

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_vector: List[float], limit: int = 5) -> List[VectorEmbedding]:
        # 'search' method deprecated/missing in this client version. Using query_points.
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        ).points
        
        return [
            VectorEmbedding(
                text=hit.payload.get("text", ""),
                vector=[], # Optimization: Don't return vector in search results unless needed
                metadata={k:v for k,v in hit.payload.items() if k != "text"}
            )
            for hit in results
        ]

