from __future__ import annotations

import asyncpg

from leaseclear.types import ChunkBase


async def search(
    conn: asyncpg.Connection,
    question: str,
    top_k: int = 20,
) -> list[ChunkBase]:
    rows = await conn.fetch(
        """--sql
        SELECT chunk_id, document_id, text, clause_label, page_number,
               char_start, char_end, token_count
        FROM chunks
        WHERE text_tsv @@ plainto_tsquery('english', $1)
        ORDER BY ts_rank(text_tsv, plainto_tsquery('english', $1)) DESC
        LIMIT $2
        """,
        question,
        top_k,
    )
    return [ChunkBase(**dict(row)) for row in rows]
