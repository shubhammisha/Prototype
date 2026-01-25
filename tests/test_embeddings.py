import unittest
from app.services.vector.embeddings import SentenceTransformerEmbeddingService, get_embedding_service
from app.schemas.vector import VectorEmbedding

class TestEmbeddingsService(unittest.TestCase):
    def setUp(self):
        # We assume the default model is all-MiniLM-L6-v2 which has 384 dimensions
        self.service = SentenceTransformerEmbeddingService()

    def test_embedding_dimensions(self):
        texts = ["Hello world", "Another sentence"]
        results = self.service.embed_batch(texts)
        
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], VectorEmbedding)
        
        # Check dimensions (384 for MiniLM)
        self.assertEqual(len(results[0].vector), 384)
        self.assertEqual(results[0].text, "Hello world")

    def test_metadata_attachment(self):
        texts = ["Test"]
        meta = [{"source": "doc1", "chunk": 0}]
        results = self.service.embed_batch(texts, metadata_list=meta)
        
        self.assertEqual(results[0].metadata["source"], "doc1")
        self.assertEqual(results[0].metadata["chunk"], 0)

    def test_factory(self):
        service = get_embedding_service()
        self.assertIsInstance(service, SentenceTransformerEmbeddingService)

if __name__ == "__main__":
    unittest.main()
