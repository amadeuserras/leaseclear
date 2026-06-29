from __future__ import annotations

from leaseclear.retrieval.fusion import reciprocal_rank_fusion
from leaseclear.types import ChunkBase


def _chunk(chunk_id: str) -> ChunkBase:
    return ChunkBase(
        chunk_id=chunk_id,
        document_id="test_lease",
        document_slug="test-lease",
        text=f"text for {chunk_id}",
        clause_label=None,
        page_number=1,
        char_start=0,
        char_end=10,
        token_count=5,
    )


def test_rrf_ranks_shared_chunks_ahead_of_single_list_hits() -> None:
    vector_results = [_chunk("a"), _chunk("b"), _chunk("c")]
    lexical_results = [_chunk("b"), _chunk("d")]

    fused = reciprocal_rank_fusion(vector_results, lexical_results)

    assert [chunk.chunk_id for chunk in fused] == ["b", "a", "d", "c"]
