from typing import List, Optional, Dict, Any
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
        If it exists but has wrong vector size, delete and recreate.
        """
        collections = self.client.get_collections()
        exists = any(c.name == self.collection_name for c in collections.collections)
        
        if exists:
            # Check config
            collection_info = self.client.get_collection(self.collection_name)
            current_size = collection_info.config.params.vectors.size
            if current_size != vector_size:
                logger.warning(f"Collection {self.collection_name} exists but has wrong size {current_size} != {vector_size}. Recreating...")
                self.client.delete_collection(self.collection_name)
                exists = False

        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=models.Distance.COSINE
                )
            )
            logger.info(f"Created collection {self.collection_name} with size {vector_size}")
            
        if exists:
            # Check if payload index exists significantly reduces API overhead
            try:
                # Get collection info again (or reuse if optimal) - here reusing
                collection_info = self.client.get_collection(self.collection_name)
                # payload_schema is a dict like {'source': PayloadSchemaInfo(...)}
                if "source" not in collection_info.payload_schema:
                     logger.info("Index for 'source' missing. Creating...")
                     self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="source",
                        field_schema=models.PayloadSchemaType.KEYWORD
                     )
                     logger.info("Created keyword index for 'source' field")
            except Exception as e:
                 logger.error(f"Failed to check/create index: {e}") 

        # If not exists, we created it above, so we should create index too
        if not exists:
             self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source",
                field_schema=models.PayloadSchemaType.KEYWORD
             )
             logger.info("Created keyword index for 'source' field (new collection)")

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

    def search(self, query_vector: List[float], limit: int = 5, filters: Optional[Dict[str, Any]] = None) -> List[VectorEmbedding]:
        # 'search' method deprecated/missing in this client version. Using query_points.
        
        query_filter = None
        if filters:
            must_conditions = []
            for key, value in filters.items():
                must_conditions.append(
                    models.FieldCondition(
                        key=key,
                        match=models.MatchValue(value=value)
                    )
                )
            if must_conditions:
                query_filter = models.Filter(must=must_conditions)
                logger.info(f"🔍 Searching with filter: {query_filter}")
            else:
                logger.info(f"⚠️ Filters provided {filters} but no conditions created.")

        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
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

