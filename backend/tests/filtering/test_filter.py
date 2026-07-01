from __future__ import annotations

from uuid import uuid4

import pytest

from leaseclear.db.connection import DbConnection
from leaseclear.filtering.filter import filter_documents
from leaseclear.ingestion.store import store_documents
from leaseclear.types import EnrichedDocument
from tests.data.corpus import CORPUS_LEASE_DOCUMENT_ID

OTHER_DOCUMENT = EnrichedDocument(
    id=uuid4(),
    slug="other-lease",
    filename="other-lease.pdf",
    pages=[],
    landlord_name="Westside Realty Holdings Inc.",
    tenant_names=["DeShawn Johnson", "Yuna Kim"],
    property_address="1142 Sunset Ridge Drive, Unit 5, Los Angeles, CA 90026",
)


@pytest.mark.real_api
async def test_filter_documents_matches_named_tenant(seed_db: DbConnection) -> None:
    await store_documents([OTHER_DOCUMENT])

    matches = await filter_documents(
        "What does DeShawn Johnson's lease say about pets?"
    )

    assert matches == [OTHER_DOCUMENT.id]


@pytest.mark.real_api
async def test_filter_documents_returns_all_for_general_question(
    seed_db: DbConnection,
) -> None:
    await store_documents([OTHER_DOCUMENT])

    matches = await filter_documents("What is the standard notice period for repairs?")

    assert set(matches) == {CORPUS_LEASE_DOCUMENT_ID, OTHER_DOCUMENT.id}
