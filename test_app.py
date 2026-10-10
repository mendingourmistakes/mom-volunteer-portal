import unittest
import os
import sqlite3
import app

class TestApp(unittest.TestCase):
    def setUp(self):
        app.init_db()

    def test_init_db(self):
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        conn.close()
        self.assertIn("users", tables)
        self.assertIn("tasks", tables)

    def test_generate_pdf_letter(self):
        pdf_output = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "Active")
        self.assertIsInstance(pdf_output, (bytes, bytearray))
        self.assertGreater(len(pdf_output), 0)

if __name__ == "__main__":
    unittest.main()
