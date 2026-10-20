import unittest
import os
import sqlite3
import pandas as pd
import app

class TestAppFunctions(unittest.TestCase):
    def test_clean_pdf_text(self):
        text = "Hello — world’s “test”"
        cleaned = app.clean_pdf_text(text)
        self.assertEqual(cleaned, "Hello - world's \"test\"")

    def test_hash_pass(self):
        hashed = app.hash_pass("mom2026")
        self.assertTrue(isinstance(hashed, str))
        self.assertEqual(len(hashed), 64)

    def test_generate_pdf_letter(self):
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertGreater(len(pdf_bytes), 0)

    def test_init_db(self):
        app.init_db()
        self.assertTrue(os.path.exists(app.DB_FILE))
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT count(*) FROM users")
        count = c.fetchone()[0]
        conn.close()
        self.assertGreater(count, 0)

if __name__ == "__main__":
    unittest.main()
