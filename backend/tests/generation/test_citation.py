from uuid import uuid4

from leaseclear.types import ChunkBase


def make_chunk(
    clause_number: str | None,
    *,
    clause_title: str | None = None,
    citation: str | None = None,
    start_page: int = 1,
    index: int = 0,
) -> ChunkBase:
    if citation is None:
        citation = f"§{clause_number}" if clause_number else f"p{start_page}"
    return ChunkBase(
        id=uuid4(),
        document_id=uuid4(),
        document_slug="test-lease",
        text="clause text",
        clause_number=clause_number,
        clause_title=clause_title,
        start_page=start_page,
        end_page=start_page,
        index=index,
        citation=citation,
    )


def test_citation_with_clause():
    chunk = make_chunk("3", clause_title="Rent")
    assert chunk.citation_id == "[test-lease §3]"


def test_citation_fallback_when_no_clause():
    chunk = make_chunk(None, start_page=1)
    assert chunk.citation_id == "[test-lease p1]"


def test_citation_versions_are_unique():
    first = make_chunk("3", citation="§3(1)", index=0)
    second = make_chunk("3", citation="§3(2)", index=1)
    assert first.citation_id != second.citation_id
