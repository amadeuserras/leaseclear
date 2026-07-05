from __future__ import annotations

from uuid import UUID, uuid4

from leaseclear.retrieval.fusion import reciprocal_rank_fusion
from leaseclear.types import ChunkBase

TEST_DOCUMENT_ID = uuid4()
CHUNK_A = uuid4()
CHUNK_B = uuid4()
CHUNK_C = uuid4()
CHUNK_D = uuid4()


def _chunk(chunk_id: UUID) -> ChunkBase:
    return ChunkBase(
        id=chunk_id,
        document_id=TEST_DOCUMENT_ID,
        document_slug="test-lease",
        text=f"text for {chunk_id}",
        clause_number=None,
        clause_label=None,
        page_number=1,
        char_start=0,
        char_end=10,
        token_count=5,
    )


def test_rrf_ranks_shared_chunks_ahead_of_single_list_hits() -> None:
    vector_results = [_chunk(CHUNK_A), _chunk(CHUNK_B), _chunk(CHUNK_C)]
    lexical_results = [_chunk(CHUNK_B), _chunk(CHUNK_D)]

    fused = reciprocal_rank_fusion(vector_results, lexical_results)

    assert [chunk.id for chunk in fused] == [CHUNK_B, CHUNK_A, CHUNK_D, CHUNK_C]
