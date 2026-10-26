import os
import sqlite3
import time
import unittest
import pandas as pd
from app import DB_FILE, clean_pdf_text, generate_pdf_letter, hash_pass, init_db


class TestAppPerformanceAndFunctionality(unittest.TestCase):
    def setUp(self):
        # Initialize DB
        init_db()

    def test_init_db_creates_tables(self):
        """Verify that init_db creates all required SQLite tables."""
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()

        expected_tables = ["users", "tasks", "announcements", "calendar_events", "discussions", "kudos", "messages", "support_tickets", "suggestions", "poll_votes"]
        for table in expected_tables:
            self.assertIn(table, tables)

    def test_clean_pdf_text(self):
        """Verify character normalization in clean_pdf_text."""
        raw_text = "Test — dash ’ quote “double”"
        cleaned = clean_pdf_text(raw_text)
        self.assertEqual(cleaned, "Test - dash ' quote \"double\"")

    def test_hash_pass(self):
        """Verify sha256 password hashing."""
        self.assertEqual(len(hash_pass("testpassword")), 64)

    def test_generate_pdf_letter_output(self):
        """Verify generate_pdf_letter generates valid PDF bytes."""
        pdf_bytes = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(bytes(pdf_bytes).startswith(b"%PDF"))

    def test_generate_pdf_letter_caching_performance(self):
        """Verify generate_pdf_letter benefits from Streamlit cache_data."""
        # Warmup / First call
        t0 = time.perf_counter()
        _ = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        t1 = time.perf_counter()
        first_call_time = t1 - t0

        # Cached calls
        t2 = time.perf_counter()
        for _ in range(10):
            _ = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
        t3 = time.perf_counter()
        avg_cached_call_time = (t3 - t2) / 10

        # Cached call should be significantly faster than uncached execution
        self.assertLess(avg_cached_call_time, first_call_time)


if __name__ == "__main__":
    unittest.main()
