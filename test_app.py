import sqlite3
from app import DB_FILE, clean_pdf_text, generate_pdf_letter, init_db


def test_clean_pdf_text():
    raw_text = "Test—Dash–Quote’Double“Quote”"
    cleaned = clean_pdf_text(raw_text)
    assert cleaned == "Test-Dash-Quote'Double\"Quote\""


def test_generate_pdf_letter_caching():
    pdf_bytes_1 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    pdf_bytes_2 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    assert pdf_bytes_1 is not None
    assert len(bytes(pdf_bytes_1)) > 0
    assert bytes(pdf_bytes_1).startswith(b"%PDF")
    # Cached call returns exact same output bytes
    assert bytes(pdf_bytes_1) == bytes(pdf_bytes_2)


def test_init_db_execution():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    user_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM tasks")
    task_count = c.fetchone()[0]
    conn.close()

    assert user_count >= 3
    assert task_count >= 3
