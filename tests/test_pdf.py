from unittest.mock import patch

from app import generate_pdf_letter


def test_generate_pdf_letter_valid_output():
    """Verify that generate_pdf_letter returns valid PDF data."""
    pdf_bytes = generate_pdf_letter("Jane Doe", "volunteer1", 12.5, 1, "Active Contributor")
    assert isinstance(pdf_bytes, (bytes, bytearray))
    assert len(pdf_bytes) > 0
    # PDF files start with %PDF
    assert bytes(pdf_bytes).startswith(b"%PDF")


def test_generate_pdf_letter_caching_behavior():
    """Verify that identical inputs hit the Streamlit cache and return identical bytes."""
    generate_pdf_letter.clear()

    with (
        patch.object(generate_pdf_letter, "_handle_cache_hit", wraps=generate_pdf_letter._handle_cache_hit) as hit_mock,
        patch.object(generate_pdf_letter, "_handle_cache_miss", wraps=generate_pdf_letter._handle_cache_miss) as miss_mock,
    ):
        # First call: cache miss
        res1 = generate_pdf_letter("Jane Doe", "vol1", 10.0, 1, "Gold")
        assert miss_mock.call_count == 1
        assert hit_mock.call_count == 0

        # Second call with same parameters: cache hit
        res2 = generate_pdf_letter("Jane Doe", "vol1", 10.0, 1, "Gold")
        assert miss_mock.call_count == 1
        assert hit_mock.call_count == 1
        assert bytes(res1) == bytes(res2)

        # Third call with altered parameters: cache miss
        res3 = generate_pdf_letter("Jane Doe", "vol1", 15.0, 1, "Gold")
        assert miss_mock.call_count == 2
        assert hit_mock.call_count == 1
        assert bytes(res1) != bytes(res3)
