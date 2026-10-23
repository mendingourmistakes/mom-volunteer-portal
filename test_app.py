import os
import sqlite3
import unittest
import pandas as pd
from app import clean_pdf_text, generate_pdf_letter, init_db, DB_FILE


class TestAppFunctions(unittest.TestCase):

    def test_clean_pdf_text(self):
        sample_text = "Testing—em dash–en dash’quote“smart”quote"
        cleaned = clean_pdf_text(sample_text)
        self.assertIn("-", cleaned)
        self.assertIn("'", cleaned)
        self.assertIn('"', cleaned)

    def test_generate_pdf_letter(self):
        pdf_bytes = generate_pdf_letter(
            full_name="Jane Doe",
            username="volunteer1",
            total_hours=12.5,
            tier=1,
            badges="🌱 Active Contributor",
        )
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertGreater(len(pdf_bytes), 0)

    def test_init_db_schema_and_indexes(self):
        init_db()
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Verify tables exist
        tables = [
            "users",
            "tasks",
            "kudos",
            "messages",
            "discussions",
            "discussion_replies",
            "support_tickets",
            "suggestions",
            "announcements",
            "calendar_events",
            "poll_votes",
        ]
        for table in tables:
            cursor.execute(
                f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'"
            )
            self.assertIsNotNone(
                cursor.fetchone(), f"Table {table} should exist"
            )

        # Check indexes exist
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
        )
        created_indexes = [row[0] for row in cursor.fetchall()]
        expected_indexes = [
            "idx_tasks_assigned_volunteer",
            "idx_tasks_status",
            "idx_messages_sender_recipient",
            "idx_discussion_replies_discussion_id",
            "idx_support_tickets_volunteer",
        ]
        for idx in expected_indexes:
            self.assertIn(
                idx, created_indexes, f"Index {idx} should exist in database"
            )

        conn.close()


if __name__ == "__main__":
    unittest.main()
