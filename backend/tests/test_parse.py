from pathlib import Path

import fitz

from leaseclear.ingestion.parse import parse_pdf


def test_parse_pdf_extracts_page_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "lease.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "RESIDENTIAL LEASE AGREEMENT")
    doc.save(pdf_path)
    doc.close()

    parsed = parse_pdf(pdf_path)

    assert parsed.source == pdf_path.resolve()
    assert parsed.page_count == 1
    assert parsed.pages[0].page_number == 1
    assert "RESIDENTIAL LEASE AGREEMENT" in parsed.pages[0].text
    assert "RESIDENTIAL LEASE AGREEMENT" in parsed.full_text


def test_parse_pdf_corpus_simple_walnut_street_2() -> None:
    pdf_file = (
        Path(__file__).resolve().parents[2]
        / "corpus"
        / "generated"
        / "simple-walnut_street_2.pdf"
    )
    parsed = parse_pdf(pdf_file)
    text = " ".join(parsed.full_text.split())

    assert parsed.page_count >= 1
    assert "RESIDENTIAL LEASE AGREEMENT" in text
    assert "Walnut Street Properties LLC" in text
    assert "410 Walnut Street, San Marcos, TX 78666" in text
    assert "Chris Nguyen" in text
    assert "410 Walnut Street, Unit 2, San Marcos, TX 78666" in text
    assert "March 1, 2026" in text
    assert "February 28, 2027" in text
    assert "$950.00" in text
