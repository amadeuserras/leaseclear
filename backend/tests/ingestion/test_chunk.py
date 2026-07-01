import uuid

from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.parse import parse_document
from leaseclear.types import AssignedDocument, PageText, UploadDocument
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

    labels = {chunk.clause_label for chunk in chunks}
    numbers = {chunk.clause_number for chunk in chunks}
    assert "" in labels
    assert None in numbers
    assert "3. Rent" in labels
    assert "5. Security Deposit" in labels
    assert "3" in numbers
    assert "5" in numbers

    rent = next(chunk for chunk in chunks if chunk.clause_number == "3")
    assert "$2,875.00" in rent.text

    for chunk in chunks:
        assert chunk.document_id == assigned.id
        assert chunk.document_slug == assigned.slug
        assert chunk.text
        assert chunk.char_end > chunk.char_start
        assert chunk.token_count > 0


def test_chunk_documents_clause_marker_split_across_lines() -> None:
    """Some PDFs extract a clause number onto its own line, separate from the
    clause title/body (e.g. "3.\nRent. Tenant shall pay..."). The chunker
    should still recognize these as clause starts."""
    page_text = (
        "1.\n"
        "Property. Landlord owns certain real property.\n"
        "2.\n"
        "Term. This Lease Agreement shall commence on March 1, 2025.\n"
        "3.\n"
        "Rent. Tenant shall pay to Landlord the sum of $2,875.00 per month.\n"
        "A.\n"
        "Delinquent Rent. Rent is overdue after the 1st.\n"
    )
    document = AssignedDocument(
        id=uuid.uuid4(),
        slug="test-lease",
        filename="test-lease.pdf",
        pages=[PageText(page_number=1, text=page_text)],
    )

    chunks = chunk_documents([document])

    numbers = {chunk.clause_number for chunk in chunks}
    labels = {chunk.clause_label for chunk in chunks}
    assert {"1", "2", "3"} <= numbers
    assert "3. Rent" in labels

    rent = next(chunk for chunk in chunks if chunk.clause_number == "3")
    assert "$2,875.00" in rent.text
