import os
import sqlite3
import unittest
from app import hash_pass, clean_pdf_text, generate_pdf_letter, init_db, DB_FILE


class TestAppFunctions(unittest.TestCase):

    def test_hash_pass(self):
        # Verify SHA-256 password hashing
        hashed = hash_pass("mom2026")
        self.assertEqual(len(hashed), 64)
        self.assertEqual(hash_pass("mom2026"), hashed)
        self.assertNotEqual(hash_pass("different"), hashed)

    def test_clean_pdf_text(self):
        # Verify clean_pdf_text replacement of non-latin1/special quote characters
        dirty = "Test — dash – quote ’ “ hello ”"
        cleaned = clean_pdf_text(dirty)
        self.assertNotIn("—", cleaned)
        self.assertNotIn("–", cleaned)
        self.assertNotIn("’", cleaned)
        self.assertNotIn("“", cleaned)
        self.assertNotIn("”", cleaned)
        self.assertIn("Test - dash - quote ' \" hello \"", cleaned)

    def test_generate_pdf_letter(self):
        # Verify PDF letter generation returns non-empty PDF bytes
        pdf_bytes = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "Active")
        self.assertIsInstance(pdf_bytes, (bytes, bytearray))
        self.assertTrue(len(pdf_bytes) > 0)
        self.assertTrue(bytes(pdf_bytes).startswith(b"%PDF"))

    def test_init_db_and_indexes(self):
        # Ensure database is initialized properly and indexes exist
        init_db()
        self.assertTrue(os.path.exists(DB_FILE))

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()

        # Verify tables exist
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in c.fetchall()]
        for expected_table in ["users", "tasks", "kudos", "messages", "discussions", "announcements"]:
            self.assertIn(expected_table, tables)

        # Verify indexes exist
        c.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = [r[0] for r in c.fetchall()]
        for expected_index in [
            "idx_tasks_assigned_volunteer",
            "idx_tasks_status",
            "idx_messages_participants",
            "idx_discussion_replies_id",
        ]:
            self.assertIn(expected_index, indexes)

        conn.close()


if __name__ == "__main__":
    unittest.main()
