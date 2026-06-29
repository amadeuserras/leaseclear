from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.parse import parse_pdf
from tests.conftest import CORPUS_LEASE_DOCUMENT_ID, CORPUS_LEASE_PDF
from tests.ingestion.data.expected_chunks_lease import EXPECTED_CHUNKS_LEASE


def test_chunk_document_corpus_lease() -> None:
    parsed = parse_pdf(CORPUS_LEASE_PDF)
    chunks = chunk_document(parsed, CORPUS_LEASE_DOCUMENT_ID)

    assert chunks == EXPECTED_CHUNKS_LEASE
