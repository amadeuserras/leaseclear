from __future__ import annotations

from typing import Any

import asyncpg

from leaseclear.ingestion.embed import embed_texts
from leaseclear.schema import RetrievedChunk


async def search(
    conn: asyncpg.Connection,
    question: str,
    top_k: int = 8,
) -> list[RetrievedChunk]:
    [query_vector] = embed_texts([question])
    rows = await conn.fetch(
        """
        SELECT chunk_id, document_id, text, clause_label, page_number,
               char_start, char_end, token_count,
               1 - (embedding <=> $1) AS similarity
        FROM chunks
        ORDER BY embedding <=> $1
        LIMIT $2
        """,
        str(query_vector),
        top_k,
    )
    return [RetrievedChunk(**dict[Any, Any](row)) for row in rows]
