import time
import unittest
import app

class TestPDFGeneration(unittest.TestCase):
    def test_generate_pdf_letter_output(self):
        pdf_bytes = app.generate_pdf_letter(
            "Jane Doe",
            "volunteer1",
            12.5,
            1,
            "🌱 Active Contributor",
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

    def test_generate_pdf_letter_caching_performance(self):
        start = time.perf_counter()
        pdf_bytes_1 = app.generate_pdf_letter(
            "Jane Doe",
            "volunteer1",
            12.5,
            1,
            "🌱 Active Contributor",
        )
        first_call_time = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        pdf_bytes_2 = app.generate_pdf_letter(
            "Jane Doe",
            "volunteer1",
            12.5,
            1,
            "🌱 Active Contributor",
        )
        cached_call_time = (time.perf_counter() - start) * 1000

        self.assertEqual(pdf_bytes_1, pdf_bytes_2)
        # Cached call should be significantly faster
        self.assertLess(cached_call_time, first_call_time)

if __name__ == "__main__":
    unittest.main()
