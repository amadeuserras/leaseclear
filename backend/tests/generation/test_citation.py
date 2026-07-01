from __future__ import annotations

from uuid import uuid4

from leaseclear.types import ChunkBase


def make_chunk(clause_number: str | None, clause_label: str | None = None) -> ChunkBase:
    return ChunkBase(
        id=uuid4(),
        document_id=uuid4(),
        document_slug="test-lease",
        text="some text",
        clause_number=clause_number,
        clause_label=clause_label,
        page_number=1,
        char_start=0,
        char_end=100,
        token_count=20,
    )


def test_citation_with_clause():
    chunk = make_chunk("3", clause_label="3. Rent")
    assert chunk.citation_id == "[test-lease §3]"


def test_citation_fallback_when_no_clause():
    chunk = make_chunk(None)
    assert chunk.citation_id == "[test-lease p.1]"
