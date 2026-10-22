import unittest
import app

class TestApp(unittest.TestCase):
    def test_clean_pdf_text(self):
        self.assertEqual(app.clean_pdf_text("hello—world"), "hello-world")
        self.assertEqual(app.clean_pdf_text("test’s"), "test's")
        self.assertEqual(app.clean_pdf_text("“quote”"), '"quote"')
        self.assertEqual(app.clean_pdf_text(""), "")

    def test_generate_pdf_letter(self):
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertTrue(isinstance(pdf_bytes, (bytes, bytearray)))
        self.assertTrue(len(pdf_bytes) > 0)

if __name__ == "__main__":
    unittest.main()
