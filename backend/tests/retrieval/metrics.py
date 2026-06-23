from __future__ import annotations

from leaseclear.types import ChunkBase


def reciprocal_rank(results: list[ChunkBase], clause_label: str) -> float:
    for position, chunk in enumerate(results, start=1):
        if chunk.clause_label == clause_label:
            return 1.0 / position
    return 0.0


def mean_reciprocal_rank(reciprocal_ranks: list[float]) -> float:
    if not reciprocal_ranks:
        return 0.0
    return sum(reciprocal_ranks) / len(reciprocal_ranks)
