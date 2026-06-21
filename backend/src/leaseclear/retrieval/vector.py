from __future__ import annotations

import asyncpg

from leaseclear.ingestion.embed import embed_texts
from leaseclear.types import RetrievedChunk


async def search(
    conn: asyncpg.Connection,
    question: str,
    top_k: int = 20,
) -> list[RetrievedChunk]:
    [query_vector] = embed_texts([question])
    rows = await conn.fetch(
        """--sql
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
    return [RetrievedChunk(**dict(row)) for row in rows]
