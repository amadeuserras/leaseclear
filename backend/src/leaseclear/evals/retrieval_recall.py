from __future__ import annotations

from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.types import ChunkBase


def has_relevance_label(item: GoldenItem) -> bool:
    """Whether `item` carries a ground-truth we can score retrieval against."""
    return item.document_slug is not None and (
        item.clause_number is not None or item.page_number is not None
    )


def is_relevant_chunk(item: GoldenItem, chunk: ChunkBase) -> bool:
    """Whether `chunk` is the ground-truth chunk for `item`."""
    if chunk.document_slug != item.document_slug:
        return False
    if item.clause_number is not None:
        return chunk.clause_number == item.clause_number
    return chunk.page_number == item.page_number


def check_recall(item: GoldenItem, retrieved: list[ChunkBase]) -> bool | None:
    """Whether the ground-truth chunk for `item` is in `retrieved`."""
    if not has_relevance_label(item):
        return None
    return any(is_relevant_chunk(item, chunk) for chunk in retrieved)
