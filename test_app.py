import unittest
import os
import sqlite3
import app

class TestApp(unittest.TestCase):
    def test_hash_pass(self):
        h1 = app.hash_pass("mom2026")
        h2 = app.hash_pass("mom2026")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_clean_pdf_text(self):
        raw = "M.O.M. – Parent’s “Hope”"
        cleaned = app.clean_pdf_text(raw)
        self.assertEqual(cleaned, 'M.O.M. - Parent\'s "Hope"')

    def test_init_db_and_indexes(self):
        # Verify init_db ran and created tables and indexes
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()

        # Check tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in c.fetchall()}
        expected_tables = {
            "users", "tasks", "kudos", "messages", "discussions",
            "discussion_replies", "support_tickets", "suggestions",
            "announcements", "calendar_events", "poll_votes"
        }
        for table in expected_tables:
            self.assertIn(table, tables)

        # Check indexes exist
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in c.fetchall()}
        expected_indexes = {"idx_users_logged_hours", "idx_tasks_status", "idx_tasks_assigned"}
        for index in expected_indexes:
            self.assertIn(index, indexes)

        conn.close()

if __name__ == "__main__":
    unittest.main()
