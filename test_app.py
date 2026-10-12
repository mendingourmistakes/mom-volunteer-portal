import os
import sqlite3
import unittest
import pandas as pd
from app import (
    DB_FILE,
    clean_pdf_text,
    generate_pdf_letter,
    hash_pass,
    init_db,
)


class TestAppPerformanceAndFunctionality(unittest.TestCase):

    def setUp(self):
        init_db()

    def test_hash_pass(self):
        h1 = hash_pass("mom2026")
        h2 = hash_pass("mom2026")
        self.assertEqual(h1, h2)
        self.assertEqual(len(h1), 64)

    def test_clean_pdf_text(self):
        text = "Hello — world ’ “test”"
        cleaned = clean_pdf_text(text)
        self.assertNotIn("—", cleaned)
        self.assertNotIn("’", cleaned)
        self.assertNotIn("“", cleaned)
        self.assertIn("-", cleaned)

    def test_generate_pdf_letter(self):
        pdf_bytes = generate_pdf_letter(
            "Jane Doe",
            "volunteer1",
            12.5,
            1,
            "🌱 Active Contributor",
        )
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertGreater(len(pdf_bytes), 0)

    def test_database_indexes_created(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [row[0] for row in c.fetchall()]
        conn.close()

        expected_indexes = [
            "idx_tasks_tier_status",
            "idx_tasks_assigned",
            "idx_discussion_replies_disc_id",
            "idx_messages_participants",
            "idx_support_tickets_volunteer",
        ]

        for idx_name in expected_indexes:
            self.assertIn(idx_name, indexes)


if __name__ == "__main__":
    unittest.main()
