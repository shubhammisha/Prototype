from abc import ABC, abstractmethod
from typing import List
# from groq import Groq # Switching to local
from app.core.config import settings
from app.schemas.vector import VectorEmbedding
# from fastembed import TextEmbedding # Removed due to Py3.13 incompatibility


class BaseEmbeddingService(ABC):
    @abstractmethod
    def embed_batch(self, texts: List[str], metadata_list: List[dict] | None = None) -> List[VectorEmbedding]:
        pass

import hashlib
import json

class HashEmbeddingService(BaseEmbeddingService):
    def __init__(self, vector_size: int = 768):
        self.vector_size = vector_size

    def embed_batch(self, texts: List[str], metadata_list: List[dict] | None = None) -> List[VectorEmbedding]:
        if not texts:
            return []
            
        results = []
        for i, text in enumerate(texts):
            # Deterministic, non-semantic embedding purely for system stability on Py3.13
            # This allows the app to RUN, but retrieval will be random/keyword-like at best.
            # We use md5 hash seeds to generate a pseudo-random vector based on text content.
            
            # 1. Seed strict
            seed = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
            
            # 2. Generate vector (pseudo-random but deterministic per text)
            # Use simple LCG or just repeating pattern
            vector = []
            current = seed
            for _ in range(self.vector_size):
                current = (current * 1103515245 + 12345) & 0x7FFFFFFF
                # Normalize roughly -1 to 1
                val = (current / 0x7FFFFFFF) * 2 - 1
                vector.append(val)
                
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
            
            results.append(VectorEmbedding(
                text=text,
                vector=vector,
                metadata=metadata
            ))
        return results

def get_embedding_service() -> BaseEmbeddingService:
    # Python 3.13 Incompatibility Fallback
    # ML libraries (torch, onnx) unavailable. 
    # Using HashEmbedding for stability.
    return HashEmbeddingService()

