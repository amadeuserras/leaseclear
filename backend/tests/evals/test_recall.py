from __future__ import annotations

from uuid import uuid4

from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.evals.retrieval_recall import check_recall
from leaseclear.types import ChunkBase


def _chunk(
    document_slug: str, clause_number: str | None, page_number: int = 1
) -> ChunkBase:
    return ChunkBase(
        id=uuid4(),
        document_id=uuid4(),
        document_slug=document_slug,
        text="some clause text",
        clause_number=clause_number,
        clause_label=None,
        page_number=page_number,
        char_start=0,
        char_end=1,
        token_count=1,
    )


def _item(
    document_slug: str | None = "texas-washington_price",
    clause_number: str | None = "3",
    page_number: int | None = 1,
    item_type: str = "answerable",
) -> GoldenItem:
    return GoldenItem(
        id="g-1",
        type=item_type,  # type: ignore[arg-type]
        question="q?",
        expected_answer="a",
        expected_refusal=False,
        document_slug=document_slug,
        clause_number=clause_number,
        page_number=page_number,
    )


def test_hit_when_clause_matches_in_retrieved_set() -> None:
    retrieved = [_chunk("texas-washington-price", "3")]
    assert check_recall(_item(), retrieved) is True


def test_miss_when_clause_absent() -> None:
    retrieved = [_chunk("texas-washington-price", "9")]
    assert check_recall(_item(), retrieved) is False


def test_miss_when_document_slug_does_not_match() -> None:
    retrieved = [_chunk("other-document", "3")]
    assert check_recall(_item(), retrieved) is False


def test_underscore_slug_normalizes_to_hyphenated_db_slug() -> None:
    # golden.jsonl slugs are written from case filenames (underscores);
    # ingestion runs filenames through slugify(), which yields hyphens.
    retrieved = [_chunk("texas-washington-price", "3")]
    assert (
        check_recall(_item(document_slug="texas-washington_price"), retrieved) is True
    )


def test_falls_back_to_page_number_when_clause_number_missing() -> None:
    retrieved = [_chunk("meridian-park-chen", None, page_number=3)]
    item = _item(document_slug="meridian-park_chen", clause_number=None, page_number=3)
    assert check_recall(item, retrieved) is True


def test_none_when_item_has_no_retrieval_target() -> None:
    item = _item(document_slug=None, clause_number=None, page_number=None)
    assert check_recall(item, []) is None


def test_none_for_unanswerable_item_without_clause() -> None:
    item = _item(clause_number=None, page_number=None, item_type="unanswerable")
    assert check_recall(item, [_chunk("texas-washington-price", "3")]) is None
