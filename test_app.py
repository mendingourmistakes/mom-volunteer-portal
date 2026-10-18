import os
import sqlite3
import unittest
import pandas as pd

# Clean up or isolate test database
TEST_DB = "mom_volunteers.db"

class TestDatabasePerformanceAndFunctionality(unittest.TestCase):

    def setUp(self):
        # Import init_db from app
        from app import init_db
        init_db()
        self.conn = sqlite3.connect(TEST_DB)
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.conn.close()

    def test_indexes_exist(self):
        """Verify that all performance indexes have been created in the database."""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in self.cursor.fetchall()}

        expected_indexes = {
            "idx_tasks_status",
            "idx_tasks_assigned_volunteer",
            "idx_discussion_replies_discussion_id",
            "idx_messages_sender_recipient",
            "idx_support_tickets_volunteer",
            "idx_users_logged_hours",
            "idx_users_role",
        }

        for idx in expected_indexes:
            self.assertIn(idx, indexes, f"Index '{idx}' was not found in sqlite_master")

    def test_query_plan_uses_indexes(self):
        """Verify that EXPLAIN QUERY PLAN uses created indexes instead of SCAN TABLE where appropriate."""
        # Query tasks by assigned_volunteer
        plan = self.cursor.execute(
            "EXPLAIN QUERY PLAN SELECT task_code, title FROM tasks WHERE assigned_volunteer = 'volunteer1'"
        ).fetchall()
        plan_str = " ".join(str(p) for p in plan)
        self.assertIn("USING INDEX idx_tasks_assigned_volunteer", plan_str)

        # Query discussion_replies by discussion_id
        plan = self.cursor.execute(
            "EXPLAIN QUERY PLAN SELECT author, content FROM discussion_replies WHERE discussion_id = 1"
        ).fetchall()
        plan_str = " ".join(str(p) for p in plan)
        self.assertIn("USING INDEX idx_discussion_replies_discussion_id", plan_str)

        # Query leaderboard ordered by logged_hours
        plan = self.cursor.execute(
            "EXPLAIN QUERY PLAN SELECT full_name, logged_hours FROM users ORDER BY logged_hours DESC LIMIT 5"
        ).fetchall()
        plan_str = " ".join(str(p) for p in plan)
        self.assertIn("idx_users_logged_hours", plan_str)
        self.assertNotIn("USE TEMP B-TREE", plan_str)

    def test_default_seeding(self):
        """Verify default users and tasks are correctly seeded."""
        users_df = pd.read_sql_query("SELECT username, role FROM users", self.conn)
        self.assertGreater(len(users_df), 0)
        self.assertIn("admin", users_df["username"].values)

        tasks_df = pd.read_sql_query("SELECT task_code, status FROM tasks", self.conn)
        self.assertGreater(len(tasks_df), 0)

if __name__ == "__main__":
    unittest.main()
