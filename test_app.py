import unittest
import os
import sqlite3
import app

class TestApp(unittest.TestCase):
    def test_hash_pass(self):
        hashed = app.hash_pass("mom2026")
        self.assertEqual(len(hashed), 64)
        self.assertIsInstance(hashed, str)

    def test_clean_pdf_text(self):
        self.assertEqual(app.clean_pdf_text(""), "")
        self.assertEqual(app.clean_pdf_text(None), "")
        self.assertEqual(app.clean_pdf_text("Test—Dash–Quote’Left“Right”"), "Test-Dash-Quote'Left\"Right\"")

    def test_init_db(self):
        app.init_db()
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()

        # Verify tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in c.fetchall()}
        required_tables = {"users", "tasks", "kudos", "messages", "discussions", "discussion_replies", "support_tickets", "suggestions", "announcements", "calendar_events", "poll_votes"}
        self.assertTrue(required_tables.issubset(tables))

        # Verify default seed data exists
        c.execute("SELECT COUNT(*) FROM users")
        self.assertGreaterEqual(c.fetchone()[0], 1)

        c.execute("SELECT COUNT(*) FROM tasks")
        self.assertGreaterEqual(c.fetchone()[0], 1)

        conn.close()

    def test_generate_pdf_letter(self):
        pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "Active")
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

if __name__ == "__main__":
    unittest.main()
