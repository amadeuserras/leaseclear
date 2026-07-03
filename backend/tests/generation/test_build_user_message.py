from __future__ import annotations

from uuid import uuid4

from leaseclear.generation.generate import _build_user_message
from leaseclear.types import DocumentMetadata


def test_user_message_includes_document_metadata(chunks):
    documents = [
        DocumentMetadata(
            id=chunks[0].document_id,
            slug="lease",
            landlord_name="Cedar Grove Rentals LLC",
            tenant_names=["Priya Nadkarni", "Daniel Osei"],
            property_address="77 Larkspur Lane, Apt 3C",
        )
    ]

    message = _build_user_message("What is the rent?", chunks, documents)

    assert "DOCUMENTS:" in message
    assert (
        "[lease] tenants: Priya Nadkarni, Daniel Osei; "
        "landlord: Cedar Grove Rentals LLC; "
        "address: 77 Larkspur Lane, Apt 3C" in message
    )
    assert message.index("DOCUMENTS:") < message.index("LEASE CLAUSES:")


def test_user_message_marks_missing_metadata_as_unknown(chunks):
    documents = [
        DocumentMetadata(
            id=uuid4(),
            slug="scan-0042",
            landlord_name=None,
            tenant_names=[],
            property_address=None,
        )
    ]

    message = _build_user_message("What is the rent?", chunks, documents)

    assert (
        "[scan-0042] tenants: unknown; landlord: unknown; address: unknown" in message
    )
