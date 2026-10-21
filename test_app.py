import os
import sqlite3
import unittest
import app

class TestApp(unittest.TestCase):

    def setUp(self):
        # Ensure fresh DB test environment if needed
        pass

    def test_hash_pass(self):
        hashed = app.hash_pass("testpassword")
        self.assertEqual(len(hashed), 64)
        self.assertIsInstance(hashed, str)

    def test_clean_pdf_text(self):
        dirty = "Test — – ’ “ ”"
        cleaned = app.clean_pdf_text(dirty)
        self.assertEqual(cleaned, 'Test - - \' " "')

    def test_init_db_creates_tables(self):
        # Ensure init_db executes cleanly
        app.init_db()
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in c.fetchall()]
        conn.close()

        expected_tables = ["users", "tasks", "kudos", "messages", "discussions", "discussion_replies", "support_tickets", "suggestions", "announcements", "calendar_events", "poll_votes"]
        for table in expected_tables:
            self.assertIn(table, tables)

    def test_init_db_caching(self):
        # Check that init_db is wrapped with Streamlit's cache_resource
        self.assertTrue(hasattr(app.init_db, "clear") or hasattr(app.init_db, "__wrapped__"))

if __name__ == "__main__":
    unittest.main()
