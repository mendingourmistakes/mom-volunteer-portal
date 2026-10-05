import unittest
import pandas as pd
from app import clean_pdf_text, generate_pdf_letter

class TestAppPerformance(unittest.TestCase):

    def test_clean_pdf_text(self):
        text = "Test — dash ’ quote “double”"
        cleaned = clean_pdf_text(text)
        self.assertEqual(cleaned, "Test - dash ' quote \"double\"")

    def test_generate_pdf_letter_returns_bytes(self):
        pdf_bytes = generate_pdf_letter(
            full_name="Jane Volunteer",
            username="jvol",
            total_hours=12.5,
            tier=2,
            badges="🌱 Active Contributor",
        )
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF-"))

    def test_generate_pdf_letter_caching_identity(self):
        # Verify cached call returns identical cached bytes
        res1 = generate_pdf_letter("Jane Volunteer", "jvol", 12.5, 2, "🌱 Active Contributor")
        res2 = generate_pdf_letter("Jane Volunteer", "jvol", 12.5, 2, "🌱 Active Contributor")
        self.assertEqual(res1, res2)

    def test_batched_discussion_replies_filtering(self):
        # Simulate batched DataFrame containing all replies across discussions
        all_replies_data = [
            {"discussion_id": 101, "author": "user1", "content": "Reply 1", "timestamp": "2026-10-01"},
            {"discussion_id": 101, "author": "user2", "content": "Reply 2", "timestamp": "2026-10-02"},
            {"discussion_id": 102, "author": "user3", "content": "Reply 3", "timestamp": "2026-10-03"},
        ]
        all_replies_df = pd.DataFrame(all_replies_data)

        # Filter in-memory for discussion 101 (batch lookup)
        disc_101_replies = all_replies_df[all_replies_df["discussion_id"] == 101]
        self.assertEqual(len(disc_101_replies), 2)
        self.assertListEqual(disc_101_replies["author"].tolist(), ["user1", "user2"])

        # Filter in-memory for discussion 103 (no replies)
        disc_103_replies = all_replies_df[all_replies_df["discussion_id"] == 103]
        self.assertTrue(disc_103_replies.empty)

if __name__ == "__main__":
    unittest.main()
