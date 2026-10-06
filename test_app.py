import unittest
from app import clean_pdf_text, generate_pdf_letter

class TestApp(unittest.TestCase):
    def test_clean_pdf_text(self):
        text = "Hello — world’s “test”"
        cleaned = clean_pdf_text(text)
        self.assertEqual(cleaned, "Hello - world's \"test\"")

    def test_generate_pdf_letter_returns_bytes(self):
        res = generate_pdf_letter("John Doe", "johndoe", 10.0, 1, "🌱 Contributor")
        self.assertIsInstance(res, bytes)
        self.assertTrue(len(res) > 0)
        self.assertTrue(res.startswith(b"%PDF"))

    def test_generate_pdf_letter_caching(self):
        res1 = generate_pdf_letter("Jane Doe", "janedoe", 15.0, 2, "🌱 Active")
        res2 = generate_pdf_letter("Jane Doe", "janedoe", 15.0, 2, "🌱 Active")
        self.assertEqual(res1, res2)

if __name__ == "__main__":
    unittest.main()
