from __future__ import annotations

from leaseclear.types import RetrievedChunk

DEFAULT_RRF_K = 60


def reciprocal_rank_fusion(
    *ranked_lists: list[RetrievedChunk],
    k: int = DEFAULT_RRF_K,
) -> list[RetrievedChunk]:
    scores: dict[str, float] = {}
    chunks: dict[str, RetrievedChunk] = {}

    for ranked_list in ranked_lists:
        for rank, chunk in enumerate(ranked_list, start=1):
            scores[chunk.chunk_id] = scores.get(chunk.chunk_id, 0.0) + 1.0 / (k + rank)
            chunks[chunk.chunk_id] = chunk

    ranked_chunk_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    return [
        RetrievedChunk(
            chunk_id=chunks[cid].chunk_id,
            document_id=chunks[cid].document_id,
            text=chunks[cid].text,
            clause_label=chunks[cid].clause_label,
            page_number=chunks[cid].page_number,
            char_start=chunks[cid].char_start,
            char_end=chunks[cid].char_end,
            token_count=chunks[cid].token_count,
            similarity=scores[cid],
        )
        for cid in ranked_chunk_ids
    ]
