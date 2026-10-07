import os
import sqlite3
import unittest
import app


class TestAppPerformanceAndDatabase(unittest.TestCase):

    def setUp(self):
        # Use an in-memory or temporary database file for isolated testing
        self.test_db = "test_mom_volunteers.db"
        app.DB_FILE = self.test_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_init_db_creates_tables_and_indexes(self):
        # Clear cache if cached
        app.init_db.clear()
        app.init_db()

        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()

        # Check tables existence
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        expected_tables = ["users", "tasks", "kudos", "messages", "discussions", "discussion_replies", "support_tickets", "suggestions", "announcements", "calendar_events", "poll_votes"]
        for table in expected_tables:
            self.assertIn(table, tables)

        # Check indexes existence
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in c.fetchall()]
        expected_indexes = [
            "idx_tasks_assigned_volunteer",
            "idx_tasks_status",
            "idx_messages_participants",
            "idx_discussion_replies_discussion_id",
            "idx_support_tickets_volunteer",
            "idx_users_logged_hours",
        ]
        for index in expected_indexes:
            self.assertIn(index, indexes)

        # Verify initial user seeding
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        self.assertGreaterEqual(user_count, 3)

        # Verify initial task seeding
        c.execute("SELECT COUNT(*) FROM tasks")
        task_count = c.fetchone()[0]
        self.assertGreaterEqual(task_count, 3)

        conn.close()

    def test_hash_pass_and_clean_pdf_text(self):
        self.assertEqual(app.hash_pass("mom2026"), app.hash_pass("mom2026"))
        self.assertNotEqual(app.hash_pass("mom2026"), app.hash_pass("wrongpass"))
        self.assertEqual(app.clean_pdf_text("— ’ “ ”"), "- ' \" \"")


if __name__ == "__main__":
    unittest.main()
