import unittest
import sqlite3
import os
import pandas as pd
from app import hash_pass, clean_pdf_text, init_db, DB_FILE

class TestAppOptimizations(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_hash_pass(self):
        hashed = hash_pass("mom2026")
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 64)

    def test_clean_pdf_text(self):
        text = "Test — dash ’ quote"
        cleaned = clean_pdf_text(text)
        self.assertNotIn("—", cleaned)
        self.assertNotIn("’", cleaned)

    def test_batch_reply_retrieval(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO discussions (author, title, category, content) VALUES ('TestUser', 'Test Topic', 'General', 'Test Content')")
        disc_id = c.lastrowid
        c.execute("INSERT INTO discussion_replies (discussion_id, author, content) VALUES (?, 'ReplyUser', 'Test Reply')", (disc_id,))
        conn.commit()

        # Execute batch retrieval logic as done in app.py
        discussions_df = pd.read_sql_query("SELECT id, author, title, category, content, timestamp FROM discussions WHERE id = ?", conn, params=(disc_id,))
        self.assertFalse(discussions_df.empty)

        replies_by_disc = {}
        disc_ids = discussions_df["id"].tolist()
        placeholders = ",".join("?" * len(disc_ids))
        all_replies_df = pd.read_sql_query(
            f"SELECT discussion_id, author, content, timestamp FROM discussion_replies WHERE discussion_id IN ({placeholders}) ORDER BY id ASC",
            conn,
            params=disc_ids
        )
        if not all_replies_df.empty:
            for d_id, group in all_replies_df.groupby("discussion_id"):
                replies_by_disc[d_id] = group

        conn.close()

        self.assertIn(disc_id, replies_by_disc)
        retrieved_replies = replies_by_disc[disc_id]
        self.assertEqual(len(retrieved_replies), 1)
        self.assertEqual(retrieved_replies.iloc[0]["content"], "Test Reply")

if __name__ == "__main__":
    unittest.main()
