import os
import sqlite3
import unittest
import pandas as pd
from app import init_db, DB_FILE

class TestAppDatabase(unittest.TestCase):
    def setUp(self):
        # Ensure fresh DB for testing
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)
        init_db()

    def tearDown(self):
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

    def test_init_db_creates_tables_and_indexes(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Verify tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in c.fetchall()]
        self.assertIn("users", tables)
        self.assertIn("tasks", tables)
        self.assertIn("discussions", tables)
        self.assertIn("discussion_replies", tables)

        # Verify indexes
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in c.fetchall()]
        self.assertIn("idx_discussion_replies_discussion_id", indexes)
        self.assertIn("idx_tasks_assigned_volunteer", indexes)
        conn.close()

    def test_discussion_replies_batch_query(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Insert test discussion
        c.execute(
            "INSERT INTO discussions (author, title, category, content) VALUES (?, ?, ?, ?)",
            ("testuser", "Test Title", "General Discussion", "Test Content")
        )
        disc_id = c.lastrowid

        # Insert test replies
        c.execute(
            "INSERT INTO discussion_replies (discussion_id, author, content) VALUES (?, ?, ?)",
            (disc_id, "responder1", "First reply")
        )
        c.execute(
            "INSERT INTO discussion_replies (discussion_id, author, content) VALUES (?, ?, ?)",
            (disc_id, "responder2", "Second reply")
        )
        conn.commit()

        # Query all discussion replies in batch
        all_replies_df = pd.read_sql_query(
            "SELECT discussion_id, author, content, timestamp FROM discussion_replies ORDER BY id ASC",
            conn
        )
        conn.close()

        self.assertEqual(len(all_replies_df), 2)
        replies_by_disc = {
            disc_id: group for disc_id, group in all_replies_df.groupby("discussion_id")
        } if not all_replies_df.empty else {}

        disc_replies = replies_by_disc.get(disc_id, pd.DataFrame())
        self.assertEqual(len(disc_replies), 2)
        self.assertListEqual(disc_replies["author"].tolist(), ["responder1", "responder2"])

if __name__ == "__main__":
    unittest.main()
