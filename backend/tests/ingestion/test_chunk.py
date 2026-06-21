from pathlib import Path

from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.parse import parse_pdf
from tests.ingestion.data.expected_chunks_lease import EXPECTED_CHUNKS_LEASE


def test_chunk_document_corpus_lease() -> None:
    pdf_file = (
        Path(__file__).resolve().parents[3] / "corpus" / "generated" / "lease.pdf"
    )

    parsed = parse_pdf(pdf_file)
    chunks = chunk_document(parsed, "lease")

    assert chunks == EXPECTED_CHUNKS_LEASE
