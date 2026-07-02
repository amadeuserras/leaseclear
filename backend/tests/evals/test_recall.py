from __future__ import annotations

from uuid import uuid4

from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.evals.retrieval_recall import check_recall
from leaseclear.types import ChunkBase


def test_check_recall_hit_and_miss() -> None:
    # golden.jsonl slugs use underscores (from case filenames); ingestion
    # slugifies filenames to hyphens, so this also checks that normalization.
    item = GoldenItem(
        id="g-1",
        type="answerable",
        question="q?",
        expected_answer="a",
        expected_refusal=False,
        document_slug="texas-washington_price",
        clause_number="3",
        page_number=1,
    )
    chunk = ChunkBase(
        id=uuid4(),
        document_id=uuid4(),
        document_slug="texas-washington-price",
        text="some clause text",
        clause_number="3",
        clause_label=None,
        page_number=1,
        char_start=0,
        char_end=1,
        token_count=1,
    )

    assert check_recall(item, [chunk]) is True
    assert check_recall(item, []) is False
