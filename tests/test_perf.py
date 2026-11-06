import sqlite3
import time
import app


def test_init_db():
    # Verify init_db initializes the database tables properly
    app.init_db()
    conn = sqlite3.connect(app.DB_FILE)
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


def test_generate_pdf_letter_output():
    pdf_bytes = app.generate_pdf_letter(
        "Test Volunteer", "volunteer1", 10.0, 1, "🌟 Active"
    )
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0
    assert bytes(pdf_bytes).startswith(b"%PDF")


def test_generate_pdf_letter_caching():
    # Calling generate_pdf_letter with identical arguments should return identical cached output
    res1 = app.generate_pdf_letter(
        "Test Volunteer 2", "volunteer2", 15.0, 2, "Active Contributor"
    )
    res2 = app.generate_pdf_letter(
        "Test Volunteer 2", "volunteer2", 15.0, 2, "Active Contributor"
    )
    assert bytes(res1) == bytes(res2)


def test_generate_pdf_letter_benchmark():
    # Benchmark to verify that cached calls are significantly faster
    args = ("Volunteer Coord", "coordinator", 25.0, 3, "🌟 Master Coordinator")

    # Prime cache / first call
    t0 = time.perf_counter()
    res1 = app.generate_pdf_letter(*args)
    t1 = time.perf_counter()
    first_duration = t1 - t0

    # 10 cached calls
    t2 = time.perf_counter()
    for _ in range(10):
        res2 = app.generate_pdf_letter(*args)
    t3 = time.perf_counter()
    avg_cached_duration = (t3 - t2) / 10

    assert bytes(res1) == bytes(res2)
    # Cached call should be faster than uncached PDF generation
    assert avg_cached_duration < first_duration
