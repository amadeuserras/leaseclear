from __future__ import annotations

from uuid import UUID

from leaseclear.retrieval.fusion import reciprocal_rank_fusion
from leaseclear.types import ChunkBase

TEST_DOCUMENT_ID = UUID("00000000-0000-4000-8000-000000000003")
CHUNK_A = UUID("00000000-0000-4000-8000-000000000010")
CHUNK_B = UUID("00000000-0000-4000-8000-000000000011")
CHUNK_C = UUID("00000000-0000-4000-8000-000000000012")
CHUNK_D = UUID("00000000-0000-4000-8000-000000000013")


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
