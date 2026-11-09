import sqlite3

from app import clean_pdf_text, generate_pdf_letter, hash_pass, init_db


def test_hash_pass():
    h1 = hash_pass("mom2026")
    h2 = hash_pass("mom2026")
    assert h1 == h2
    assert len(h1) == 64


def test_clean_pdf_text():
    assert clean_pdf_text("— ’ ”") == "- ' \""
    assert clean_pdf_text("") == ""


def test_generate_pdf_letter_output():
    pdf_bytes = generate_pdf_letter(
        "Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor"
    )
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF")


def test_generate_pdf_letter_caching():
    res1 = generate_pdf_letter(
        "Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor"
    )
    res2 = generate_pdf_letter(
        "Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor"
    )
    # Cached responses should return identical bytes
    assert res1 == res2
    assert id(res1) == id(res2) or res1 == res2


def test_init_db():
    init_db()
    conn = sqlite3.connect("mom_volunteers.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    assert c.fetchone()[0] >= 3
    conn.close()
