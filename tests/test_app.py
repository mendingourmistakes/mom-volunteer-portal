import os
import sqlite3
from app import generate_pdf_letter, init_db, DB_FILE


def test_generate_pdf_letter_output():
    pdf_bytes = generate_pdf_letter(
        full_name="Jane Doe",
        username="volunteer1",
        total_hours=12.5,
        tier=1,
        badges="🌱 Active Contributor",
    )
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0
    # PDF magic header
    assert bytes(pdf_bytes).startswith(b"%PDF")


def test_generate_pdf_letter_caching():
    pdf_1 = generate_pdf_letter(
        full_name="Jane Doe",
        username="volunteer1",
        total_hours=12.5,
        tier=1,
        badges="🌱 Active Contributor",
        date_str="October 31, 2026",
    )
    pdf_2 = generate_pdf_letter(
        full_name="Jane Doe",
        username="volunteer1",
        total_hours=12.5,
        tier=1,
        badges="🌱 Active Contributor",
        date_str="October 31, 2026",
    )
    assert bytes(pdf_1) == bytes(pdf_2)


def test_init_db_execution():
    # Ensure init_db executes without error and creates required tables
    init_db()
    assert os.path.exists(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in c.fetchall()}
    conn.close()

    expected_tables = {
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
    }
    assert expected_tables.issubset(tables)
