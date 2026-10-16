import os
import sqlite3
import unittest
import pandas as pd

import app


class TestAppPerformanceAndDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure database is initialized
        app.init_db()

    def test_hash_pass(self):
        h1 = app.hash_pass("mom2026")
        h2 = app.hash_pass("mom2026")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_clean_pdf_text(self):
        raw = "Hello — world ’ test “ quote ”"
        cleaned = app.clean_pdf_text(raw)
        self.assertIn("Hello - world ' test \" quote \"", cleaned)

    def test_db_indexes_exist(self):
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in c.fetchall()}
        conn.close()

        expected_indexes = {
            "idx_discussion_replies_disc_id",
            "idx_tasks_status",
            "idx_tasks_assigned_vol",
            "idx_messages_sender_recip",
            "idx_support_tickets_vol",
        }
        for idx in expected_indexes:
            self.assertIn(idx, indexes, f"Index {idx} missing from database")

    def test_batch_discussion_replies_fetch(self):
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO discussions (author, title, category, content) VALUES (?, ?, ?, ?)",
            ("testuser", "Test Topic", "General", "Test content"),
        )
        disc_id = c.lastrowid
        c.execute(
            "INSERT INTO discussion_replies (discussion_id, author, content) VALUES (?, ?, ?)",
            (disc_id, "replier", "Test reply message"),
        )
        conn.commit()

        # Batch query matching app logic
        discussions_df = pd.read_sql_query(
            "SELECT id, author, title, category, content, timestamp FROM discussions WHERE id = ?",
            conn,
            params=(disc_id,),
        )
        all_replies_df = pd.read_sql_query(
            "SELECT discussion_id, author, content, timestamp FROM discussion_replies WHERE discussion_id = ?",
            conn,
            params=(disc_id,),
        )
        conn.close()

        replies_map = {}
        if not all_replies_df.empty:
            for r in all_replies_df.to_dict("records"):
                replies_map.setdefault(r["discussion_id"], []).append(r)

        self.assertIn(disc_id, replies_map)
        self.assertEqual(len(replies_map[disc_id]), 1)
        self.assertEqual(replies_map[disc_id][0]["author"], "replier")
        self.assertEqual(replies_map[disc_id][0]["content"], "Test reply message")


if __name__ == "__main__":
    unittest.main()
