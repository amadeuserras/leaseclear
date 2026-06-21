from __future__ import annotations

import asyncpg

from leaseclear.retrieval import fusion, lexical_search, vector_search
from leaseclear.types import RetrievedChunk

VECTOR_TOP_K = 20
LEXICAL_TOP_K = 20
DEFAULT_TOP_K = 8


async def search(
    conn: asyncpg.Connection,
    question: str,
    top_k: int = DEFAULT_TOP_K,
) -> list[RetrievedChunk]:
    vector_results = await vector_search.search(conn, question, top_k=VECTOR_TOP_K)
    lexical_results = await lexical_search.search(conn, question, top_k=LEXICAL_TOP_K)
    fused = fusion.reciprocal_rank_fusion(vector_results, lexical_results)
    return fused[:top_k]
