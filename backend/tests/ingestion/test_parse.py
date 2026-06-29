from leaseclear.ingestion.parse import ParsedDocument, parse_pdf
from tests.ingestion.corpus import CORPUS_LEASE_PDF
from tests.ingestion.data.expected_parsed_lease import EXPECTED_PARSED_LEASE_PAGES


def test_parse_pdf_corpus_lease() -> None:
    parsed = parse_pdf(CORPUS_LEASE_PDF)

    assert parsed == ParsedDocument(
        source=CORPUS_LEASE_PDF.resolve(),
        pages=EXPECTED_PARSED_LEASE_PAGES,
    )
