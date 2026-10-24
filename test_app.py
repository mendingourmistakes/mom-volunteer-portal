import os
import sqlite3
import unittest
import app

class TestAppDatabase(unittest.TestCase):
    def setUp(self):
        # Use test database file for isolation
        self.test_db = "test_mom_volunteers.db"
        app.DB_FILE = self.test_db
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        # Clear Streamlit cache for init_db if cached
        app.init_db.clear()

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_init_db_creates_tables_and_indexes(self):
        """Verify init_db creates all required tables and indexes."""
        app.init_db()

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()

        # Check expected tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        expected_tables = {
            "users", "tasks", "kudos", "messages", "discussions",
            "discussion_replies", "support_tickets", "suggestions",
            "announcements", "calendar_events", "poll_votes"
        }
        for table in expected_tables:
            self.assertIn(table, tables, f"Table {table} should exist in database.")

        # Check expected performance indexes exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        expected_indexes = {
            "idx_tasks_assigned_volunteer",
            "idx_tasks_status",
            "idx_messages_sender_recipient",
            "idx_discussion_replies_discussion_id",
            "idx_support_tickets_volunteer",
        }
        for index_name in expected_indexes:
            self.assertIn(index_name, indexes, f"Index {index_name} should exist in database.")

        # Verify seed data inserted
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        self.assertGreater(user_count, 0, "Users table should have default seed data.")

        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        self.assertGreater(task_count, 0, "Tasks table should have default seed data.")

        conn.close()

    def test_init_db_idempotent(self):
        """Verify calling init_db multiple times is safe and idempotent."""
        app.init_db()
        app.init_db.clear()
        app.init_db()

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        self.assertEqual(user_count, 3, "Reseeding should not create duplicate default users.")
        conn.close()

if __name__ == "__main__":
    unittest.main()
