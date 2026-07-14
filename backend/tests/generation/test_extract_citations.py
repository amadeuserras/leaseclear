from uuid import uuid4

from leaseclear.generation.parse import (
    extract_citation_ids,
    generation_result_from_answer,
    resolve_citations,
)
from leaseclear.types import ChunkBase


def test_extract_citation_ids_preserves_order_and_dedupes() -> None:
    text = (
        "Rent is due on the first [lease §3]. "
        "The deposit is separate [lease §4]. "
        "Rent again [lease §3]."
    )
    assert extract_citation_ids(text) == ["[lease §3]", "[lease §4]"]


def test_extract_citation_ids_supports_versions_and_pages() -> None:
    text = "See [doc §5(2)] and preamble [doc p1]."
    assert extract_citation_ids(text) == ["[doc §5(2)]", "[doc p1]"]


def test_generation_result_from_answer_builds_citations() -> None:
    result = generation_result_from_answer("Pay [lease §3] monthly.")
    assert result.answer == "Pay [lease §3] monthly."
    assert [c.id for c in result.citations] == ["[lease §3]"]


def test_resolve_citations_skips_unknown() -> None:
    chunk = ChunkBase(
        id=uuid4(),
        document_id=uuid4(),
        document_slug="lease",
        text="rent",
        clause_number="3",
        clause_title="Rent",
        start_page=1,
        end_page=1,
        index=0,
        citation="§3",
    )
    resolved = resolve_citations(["[lease §3]", "[lease §99]"], [chunk])
    assert resolved == [chunk]
