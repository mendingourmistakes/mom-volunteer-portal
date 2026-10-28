import unittest
import app

class TestAppPdfGeneration(unittest.TestCase):
    def test_generate_pdf_letter_returns_bytes(self):
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_generate_pdf_letter_caching(self):
        res1 = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        res2 = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertEqual(res1, res2)

if __name__ == "__main__":
    unittest.main()
