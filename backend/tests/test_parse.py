from pathlib import Path

from leaseclear.ingestion.parse import ParsedDocument, parse_pdf
from tests.fixtures.expected_parsed_lease import EXPECTED_PARSED_LEASE_PAGES


def test_parse_pdf_corpus_lease() -> None:
    pdf_file = (
        Path(__file__).resolve().parents[2] / "corpus" / "generated" / "lease.pdf"
    )

    parsed = parse_pdf(pdf_file)

    assert parsed == ParsedDocument(
        source=pdf_file.resolve(),
        pages=EXPECTED_PARSED_LEASE_PAGES,
    )
