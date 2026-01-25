import unittest
from app.services.document.chunker import DocumentChunker

class TestDocumentChunker(unittest.TestCase):
    def setUp(self):
        self.chunker = DocumentChunker()
        
    def test_small_text(self):
        text = "Hello world"
        chunks = self.chunker.chunk(text, chunk_size=10)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], text)

    def test_chunk_split(self):
        # Create a text that is definitely longer than 5 tokens
        # "Hello world" is 2 tokens. Repeated 10 times is 20 tokens.
        text = "Hello world " * 10
        chunk_size = 5
        overlap = 0
        
        chunks = self.chunker.chunk(text, chunk_size=chunk_size, chunk_overlap=overlap)
        
        # We expect multiple chunks
        self.assertTrue(len(chunks) > 1)
        
        # Verify first chunk token count
        first_tokens = self.chunker.encoding.encode(chunks[0])
        self.assertLessEqual(len(first_tokens), chunk_size)

    def test_overlap(self):
        # 0 1 2 3 4 5 6 7 8 9 (integers as tokens for simplicity conceptualization)
        # Size 5, Overlap 2
        # Chunk 1: 0-5
        # Chunk 2: 3-8 (Start at 5-2=3)
        
        text = "one two three four five six seven eight nine ten"
        chunk_size = 5
        overlap = 2
        
        chunks = self.chunker.chunk(text, chunk_size=chunk_size, chunk_overlap=overlap)
        
        # Check that end of chunk 0 appears in chunk 1
        # Note: Exact string matching is tricky due to spacing, so we check token overlap
        tokens0 = self.chunker.encoding.encode(chunks[0])
        tokens1 = self.chunker.encoding.encode(chunks[1])
        
        # The last 'overlap' tokens of chunk 0 should match first 'overlap' tokens of chunk 1
        suffix0 = tokens0[-overlap:]
        prefix1 = tokens1[:overlap]
        
        self.assertEqual(suffix0, prefix1)

if __name__ == "__main__":
    unittest.main()
