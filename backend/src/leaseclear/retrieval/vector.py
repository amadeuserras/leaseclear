from __future__ import annotations

import asyncpg

from leaseclear.ingestion.embed import embed_texts
from leaseclear.types import ChunkBase


async def search(
    conn: asyncpg.Connection,
    question: str,
    top_k: int = 20,
    similarity_floor: float | None = 0.35,
) -> list[ChunkBase]:
    [query_vector] = embed_texts([question])
    rows = await conn.fetch(
        """--sql
        SELECT chunk_id, document_id, text, clause_label, page_number,
               char_start, char_end, token_count
        FROM chunks
        WHERE ($3::float IS NULL OR 1 - (embedding <=> $1) >= $3)
        ORDER BY embedding <=> $1
        LIMIT $2
        """,
        str(query_vector),
        top_k,
        similarity_floor,
    )
    return [ChunkBase(**dict(row)) for row in rows]
