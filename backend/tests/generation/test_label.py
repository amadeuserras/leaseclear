from __future__ import annotations

from uuid import uuid4

from leaseclear.generation.label import label_chunks
from leaseclear.types import ChunkBase


def make_chunk(document_id: str, clause_label: str | None) -> ChunkBase:
    return ChunkBase(
        chunk_id=str(uuid4()),
        document_id=document_id,
        document_slug="test-lease",
        text="some text",
        clause_label=clause_label,
        page_number=1,
        char_start=0,
        char_end=100,
        token_count=20,
    )


def test_label_with_clause():
    chunks = [make_chunk("test_lease", "3. Rent")]
    result = label_chunks(chunks)
    assert result[0].citation_id == "[test_lease §3. Rent]"


def test_label_fallback_when_no_clause():
    chunks = [make_chunk("test_lease", None)]
    result = label_chunks(chunks)
    assert result[0].citation_id == "[test_lease p.1]"
