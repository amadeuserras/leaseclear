from __future__ import annotations

from leaseclear.types import RetrievedChunk

SIMILARITY_FLOOR = 0.35


def passes_similarity_floor(
    chunks: list[RetrievedChunk],
    threshold: float = SIMILARITY_FLOOR,
) -> bool:
    if not chunks:
        return False
    return max(chunk.similarity for chunk in chunks) >= threshold
