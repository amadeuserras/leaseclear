from __future__ import annotations

from leaseclear.types import ChunkBase

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    *ranked_lists: list[ChunkBase],
    k: int = DEFAULT_RRF_K,
) -> list[ChunkBase]:
    scores: dict[str, float] = {}
    chunks: dict[str, ChunkBase] = {}

    for ranked_list in ranked_lists:
        for rank, chunk in enumerate(ranked_list, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (k + rank)
            chunks[chunk.chunk_id] = chunk

    ranked_chunk_ids: list[str] = sorted(
        scores, key=lambda cid: scores[cid], reverse=True
    )

    return [chunks[i] for i in ranked_chunk_ids]
