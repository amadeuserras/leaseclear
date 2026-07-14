from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from leaseclear.ingestion.slug import make_document_slug
from leaseclear.types import EmbeddedChunk, EnrichedDocument

_DATA_DIR = Path(__file__).resolve().parent

CORPUS_LEASE_PDF = _DATA_DIR / "test_lease.pdf"
CORPUS_LEASE_DOCUMENT_ID = UUID("00000000-0000-4000-8000-000000000001")
TEST_LEASE_CHUNKS_PATH = _DATA_DIR / "test_lease_chunks.json"

SEED_DOCUMENT = EnrichedDocument(
    id=CORPUS_LEASE_DOCUMENT_ID,
    slug=make_document_slug(CORPUS_LEASE_PDF.name),
    filename=CORPUS_LEASE_PDF.name,
    pages=[],
    landlord_name="Cedar Grove Rentals LLC",
    tenant_names=["Priya Nadkarni", "Daniel Osei"],
    property_address="77 Larkspur Lane, Apt 3C, Port Marlow, CA 94066",
)

_fixture_data = json.loads(TEST_LEASE_CHUNKS_PATH.read_text())
SEED_CHUNKS = [
    EmbeddedChunk(
        id=UUID(chunk["id"]),
        document_id=UUID(chunk["document_id"]),
        document_slug=chunk["document_slug"],
        text=chunk["text"],
        clause_number=chunk["clause_number"],
        clause_title=chunk["clause_title"],
        start_page=chunk["start_page"],
        end_page=chunk["end_page"],
        index=chunk["index"],
        citation=chunk["citation"],
        embedding=chunk["embedding"],
    )
    for chunk in _fixture_data["chunks"]
]
