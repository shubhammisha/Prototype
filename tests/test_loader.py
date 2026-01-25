import unittest
from app.services.document.loader import PDFLoader

class TestPDFLoader(unittest.TestCase):
    def setUp(self):
        self.loader = PDFLoader()
        
    def test_clean_text_basic(self):
        dirty_text = "Hello   World.  \n\n\nThis is a test."
        clean = self.loader._clean_text(dirty_text)
        self.assertEqual(clean, "Hello World.\n\nThis is a test.")

    def test_remove_page_numbers(self):
        text_with_page = "Content here.\nPage 10\nMore content."
        clean = self.loader._clean_text(text_with_page, page_num=10)
        self.assertNotIn("Page 10", clean)
        self.assertIn("Content here.", clean)

    def test_remove_dash_page_numbers(self):
        text = "Start.\n- 5 -\nEnd."
        clean = self.loader._clean_text(text)
        self.assertNotIn("- 5 -", clean)

    def test_keep_short_content(self):
        # Ensure we don't delete "Title" or "1." lists
        text = "Title\n\n1. Item"
        clean = self.loader._clean_text(text)
        self.assertIn("Title", clean)
        self.assertIn("1. Item", clean)

if __name__ == "__main__":
    unittest.main()
