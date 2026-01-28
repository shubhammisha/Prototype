
import unittest
from unittest.mock import MagicMock, patch
from app.services.vector.store import QdrantVectorStore
from qdrant_client.http import models

class TestQdrantFiltering(unittest.TestCase):
    @patch('app.services.vector.store.QdrantClient')
    @patch('app.services.vector.store.settings')
    def test_search_with_filters(self, mock_settings, mock_client_class):
        # Setup
        mock_settings.VECTOR_DB_URL = "http://localhost:6333"
        mock_settings.VECTOR_COLLECTION_NAME = "test_collection"
        
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        
        # Instantiate Store
        store = QdrantVectorStore()
        
        # Execute Search with Filters
        query_vector = [0.1, 0.2, 0.3]
        filters = {"source": "test_doc.pdf"}
        
        store.search(query_vector=query_vector, filters=filters)
        
        # Verify call arguments
        call_args = mock_client.query_points.call_args
        _, kwargs = call_args
        
        # Check if query_filter was constructed correctly
        query_filter = kwargs.get('query_filter')
        self.assertIsInstance(query_filter, models.Filter)
        self.assertTrue(len(query_filter.must) > 0)
        
        condition = query_filter.must[0]
        self.assertIsInstance(condition, models.FieldCondition)
        self.assertEqual(condition.key, "source")
        self.assertEqual(condition.match.value, "test_doc.pdf")
        
        print("\n✅ Unit Test Passed: Qdrant query_points called with correct Filter object.")

if __name__ == '__main__':
    unittest.main()
