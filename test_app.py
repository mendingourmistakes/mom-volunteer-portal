import os
import unittest
import app

class TestPDFLetterGeneration(unittest.TestCase):
    def test_generate_pdf_letter_output(self):
        pdf_bytes = app.generate_pdf_letter(
            "Test User",
            "testuser",
            10.0,
            1,
            "Active Contributor"
        )
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertGreater(len(pdf_bytes), 0)

    def test_generate_pdf_letter_caching(self):
        pdf1 = app.generate_pdf_letter("Test User", "testuser", 10.0, 1, "Active Contributor")
        pdf2 = app.generate_pdf_letter("Test User", "testuser", 10.0, 1, "Active Contributor")
        self.assertEqual(bytes(pdf1), bytes(pdf2))

if __name__ == "__main__":
    unittest.main()
