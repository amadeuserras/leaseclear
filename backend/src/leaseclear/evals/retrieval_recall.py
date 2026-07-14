from __future__ import annotations

from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.types import ChunkBase


def has_relevance_label(item: GoldenItem) -> bool:
    """Whether `item` carries a ground-truth we can score retrieval against."""
    return bool(item.citation_ids)


def is_relevant_chunk(item: GoldenItem, chunk: ChunkBase) -> bool:
    """Whether `chunk` is one of the ground-truth chunks for `item`."""
    return chunk.citation_id in item.citation_ids


def check_recall(item: GoldenItem, retrieved: list[ChunkBase]) -> bool | None:
    """Whether the ground-truth chunk for `item` is in `retrieved`."""
    if not has_relevance_label(item):
        return None
    return any(is_relevant_chunk(item, chunk) for chunk in retrieved)
