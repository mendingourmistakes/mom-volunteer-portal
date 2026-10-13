import unittest
from app import generate_pdf_letter, hash_pass, clean_pdf_text

class TestAppPerformanceAndUtils(unittest.TestCase):

    def test_clean_pdf_text(self):
        raw = "Hello — world ’ “test”"
        cleaned = clean_pdf_text(raw)
        self.assertNotIn("—", cleaned)
        self.assertIn("-", cleaned)
        self.assertNotIn("’", cleaned)
        self.assertIn("'", cleaned)

    def test_hash_pass(self):
        self.assertEqual(len(hash_pass("mom2026")), 64)

    def test_generate_pdf_letter(self):
        pdf_bytes1 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        pdf_bytes2 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")

        self.assertIsInstance(pdf_bytes1, (bytes, bytearray))
        self.assertTrue(len(pdf_bytes1) > 0)
        # Verify cached output is identical
        self.assertEqual(bytes(pdf_bytes1), bytes(pdf_bytes2))

if __name__ == "__main__":
    unittest.main()
