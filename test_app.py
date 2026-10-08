import unittest
import app

class TestAppPerformanceAndPDF(unittest.TestCase):
    def test_clean_pdf_text(self):
        text = "Hello — world’s “best” test"
        cleaned = app.clean_pdf_text(text)
        self.assertEqual(cleaned, 'Hello - world\'s "best" test')

    def test_generate_pdf_letter(self):
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertTrue(isinstance(pdf_bytes, (bytes, bytearray)))
        self.assertGreater(len(pdf_bytes), 1000)

if __name__ == "__main__":
    unittest.main()
