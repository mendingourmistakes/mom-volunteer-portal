import sqlite3
import app


def test_hash_pass():
    h1 = app.hash_pass("mom2026")
    assert isinstance(h1, str)
    assert len(h1) == 64
    assert h1 == app.hash_pass("mom2026")
    assert h1 != app.hash_pass("other_password")


def test_clean_pdf_text():
    raw = "Special—dash and quotes’ and “double”"
    cleaned = app.clean_pdf_text(raw)
    assert "—" not in cleaned
    assert "’" not in cleaned
    assert "“" not in cleaned
    assert "”" not in cleaned
    assert cleaned == "Special-dash and quotes' and \"double\""
    assert app.clean_pdf_text("") == ""
    assert app.clean_pdf_text(None) == ""


def test_generate_pdf_letter_caching_and_output():
    # Clear cache before testing
    app.generate_pdf_letter.clear()

    res1 = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    assert isinstance(res1, (bytes, bytearray))
    assert len(res1) > 0
    # PDF files start with %PDF-
    assert bytes(res1).startswith(b"%PDF-")

    # Second call with same parameters should return identical cached output
    res2 = app.generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    assert bytes(res1) == bytes(res2)


def test_init_db():
    # Calling init_db multiple times should be safe and idempotent
    app.init_db()
    app.init_db()

    conn = sqlite3.connect(app.DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count_users = c.fetchone()[0]
    assert count_users >= 3

    c.execute("SELECT COUNT(*) FROM tasks")
    count_tasks = c.fetchone()[0]
    assert count_tasks >= 3
    conn.close()
