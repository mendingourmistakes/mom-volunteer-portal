from app import clean_pdf_text, generate_pdf_letter


def test_clean_pdf_text_replaces_special_chars():
    raw_text = "M.O.M.—Parent’s “Guide” – 2026"
    cleaned = clean_pdf_text(raw_text)
    assert cleaned == 'M.O.M.-Parent\'s "Guide" - 2026'


def test_clean_pdf_text_empty():
    assert clean_pdf_text("") == ""
    assert clean_pdf_text(None) == ""


def test_generate_pdf_letter_returns_bytes_and_caches():
    # First invocation (computes PDF)
    pdf1 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    assert isinstance(pdf1, (bytes, bytearray))
    assert len(pdf1) > 0
    assert bytes(pdf1).startswith(b"%PDF")

    # Second invocation with same args (served from cache)
    pdf2 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    assert bytes(pdf1) == bytes(pdf2)


def test_generate_pdf_letter_updates_on_param_change():
    pdf1 = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "🌱 Active Contributor")
    pdf2 = generate_pdf_letter("Jane Doe", "volunteer1", 15.0, 2, "🏅 Silver Contributor")
    assert bytes(pdf1) != bytes(pdf2)
