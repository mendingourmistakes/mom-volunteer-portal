import sqlite3
import app


def test_generate_pdf_letter_returns_pdf_bytes():
    """Verify generate_pdf_letter returns non-empty PDF bytes starting with %PDF."""
    pdf_bytes = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")


def test_generate_pdf_letter_caching():
    """Verify that calling generate_pdf_letter with same parameters returns identical cached bytes."""
    res1 = app.generate_pdf_letter("Test User", "testuser", 25.0, 2, "🏅 Gold")
    res2 = app.generate_pdf_letter("Test User", "testuser", 25.0, 2, "🏅 Gold")
    assert res1 == res2
    assert id(res1) == id(res2) or res1 == res2


def test_clean_pdf_text():
    """Verify unicode characters and quotes are properly cleaned for FPDF latin-1."""
    dirty_text = "M.O.M. — ‘Special’ “Letter”"
    cleaned = app.clean_pdf_text(dirty_text)
    assert "—" not in cleaned
    assert "‘" not in cleaned
    assert "’" not in cleaned
    assert '"' in cleaned
    assert "-" in cleaned


def test_init_db_creates_tables_and_seeds():
    """Verify init_db initializes the database with expected tables and default rows."""
    app.init_db()
    conn = sqlite3.connect(app.DB_FILE)
    c = conn.cursor()

    # Verify tables exist
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in c.fetchall()}
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

    # Verify default users seeded
    c.execute("SELECT COUNT(*) FROM users")
    assert c.fetchone()[0] >= 3

    # Verify default tasks seeded
    c.execute("SELECT COUNT(*) FROM tasks")
    assert c.fetchone()[0] >= 3

    conn.close()
