import unittest
import app

class TestAppPerformanceAndUtility(unittest.TestCase):
    def test_clean_pdf_text(self):
        text = "Hello — world ’ test “ quote ”"
        cleaned = app.clean_pdf_text(text)
        self.assertEqual(cleaned, 'Hello - world \' test " quote "')

    def test_hash_pass(self):
        hashed = app.hash_pass("mom2026")
        self.assertEqual(len(hashed), 64)

    def test_generate_pdf_letter_output(self):
        # Ensure generate_pdf_letter returns bytes or bytearray
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertTrue(isinstance(pdf_bytes, (bytes, bytearray)))
        self.assertGreater(len(pdf_bytes), 0)

if __name__ == '__main__':
    unittest.main()
