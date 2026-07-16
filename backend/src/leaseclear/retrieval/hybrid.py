from __future__ import annotations

from uuid import UUID

from leaseclear.retrieval import fusion, trigram, vector
from leaseclear.types import ChunkBase

VECTOR_TOP_K = 20
TRIGRAM_TOP_K = 20
DEFAULT_TOP_K = 8


async def search(
    question: str,
    top_k: int = DEFAULT_TOP_K,
    document_ids: list[UUID] | None = None,
) -> list[ChunkBase]:
    vector_results = await vector.search(
        question, top_k=VECTOR_TOP_K, document_ids=document_ids
    )
    trigram_results = await trigram.search(
        question, top_k=TRIGRAM_TOP_K, document_ids=document_ids
    )
    fused = fusion.reciprocal_rank_fusion(vector_results, trigram_results)
    return fused[:top_k]
