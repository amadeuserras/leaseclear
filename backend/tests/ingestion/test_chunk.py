from uuid import UUID

from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.parse import parse_document
from leaseclear.types import UploadDocument
from tests.conftest import CORPUS_LEASE_PDF


def test_chunk_documents_corpus_lease() -> None:
    upload = UploadDocument(
        path=str(CORPUS_LEASE_PDF),
        filename=CORPUS_LEASE_PDF.name,
    )
    parsed = parse_document(upload)
    assigned = assign_document(parsed, set())
    chunks = chunk_documents([assigned])

    assert len(chunks) >= 10

    labels = {chunk.clause_label for chunk in chunks}
    assert "" in labels
    assert "3. Rent" in labels
    assert "5. Security Deposit" in labels

    rent = next(chunk for chunk in chunks if chunk.clause_label == "3. Rent")
    assert "$2,875.00" in rent.text

    for chunk in chunks:
        UUID(chunk.chunk_id)
        assert chunk.document_id == assigned.id
        assert chunk.document_slug == assigned.slug
        assert chunk.text
        assert chunk.char_end > chunk.char_start
        assert chunk.token_count > 0
