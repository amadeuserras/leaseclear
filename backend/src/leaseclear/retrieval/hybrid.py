from __future__ import annotations

from leaseclear.retrieval import fusion, lexical, vector
from leaseclear.types import ChunkBase

VECTOR_TOP_K = 20
LEXICAL_TOP_K = 20
DEFAULT_TOP_K = 8


async def search(
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[ChunkBase]:
    vector_results = await vector.search(question, top_k=VECTOR_TOP_K)
    lexical_results = await lexical.search(question, top_k=LEXICAL_TOP_K)
    fused = fusion.reciprocal_rank_fusion(vector_results, lexical_results)
    return fused[:top_k]
