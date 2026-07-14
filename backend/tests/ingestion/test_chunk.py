from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.parse import parse_document
from leaseclear.types import UploadDocument
from tests.data.corpus import CORPUS_LEASE_PDF


def test_chunk_documents_corpus_lease() -> None:
    upload = UploadDocument(
        path=str(CORPUS_LEASE_PDF),
        filename=CORPUS_LEASE_PDF.name,
    )
    parsed = parse_document(upload)
    assigned = assign_document(parsed, set())
    chunks = chunk_documents([assigned])

    assert len(chunks) >= 10

    titles = {chunk.clause_title for chunk in chunks}
    numbers = {chunk.clause_number for chunk in chunks}
    citations = {chunk.citation for chunk in chunks}

    assert None in numbers
    assert "Rent" in titles
    assert "Security Deposit" in titles
    assert "3" in numbers
    assert "5" in numbers
    assert any(c == "§3" or c.startswith("§3(") for c in citations)
    assert any(c == "§5" or c.startswith("§5(") for c in citations)

    rent = next(chunk for chunk in chunks if chunk.clause_number == "3")
    assert "$2,875.00" in rent.text

    for index, chunk in enumerate(chunks):
        assert chunk.document_id == assigned.id
        assert chunk.document_slug == assigned.slug
        assert chunk.text
        assert chunk.index == index
        assert chunk.citation
        assert chunk.start_page >= 1
        assert chunk.end_page >= chunk.start_page
