import unittest
import app

class TestPDFGeneration(unittest.TestCase):
    def test_generate_pdf_letter(self):
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertTrue(len(pdf_bytes) > 0)

    def test_cached_pdf_generation(self):
        pdf1 = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        pdf2 = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertEqual(pdf1, pdf2)

if __name__ == "__main__":
    unittest.main()
