from __future__ import annotations

from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.types import ChunkBase


def check_recall(item: GoldenItem, retrieved: list[ChunkBase]) -> bool | None:
    """Whether the ground-truth clause for `item` is in `retrieved`.

    Returns None when the item has no ground-truth clause/page to check
    against (e.g. unanswerable items), so callers can exclude it from
    recall@8 rather than counting it as a miss.
    """
    target_slug = item.canonical_document_slug
    if target_slug is None or (item.clause_number is None and item.page_number is None):
        return None

    for chunk in retrieved:
        if chunk.document_slug != target_slug:
            continue
        if item.clause_number is not None:
            if chunk.clause_number == item.clause_number:
                return True
        elif chunk.page_number == item.page_number:
            return True
    return False
