import os
import sqlite3
import unittest
import app

class TestApp(unittest.TestCase):
    def test_hash_pass(self):
        hashed = app.hash_pass("mom2026")
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 64)

    def test_init_db(self):
        # Ensure init_db runs without error
        app.init_db()
        conn = sqlite3.connect(app.DB_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users")
        user_count = c.fetchone()[0]
        conn.close()
        self.assertGreater(user_count, 0)

if __name__ == "__main__":
    unittest.main()
