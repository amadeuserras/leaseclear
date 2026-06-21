from __future__ import annotations

import asyncpg

from leaseclear.schema import EmbeddedChunk


async def store_chunks(
    conn: asyncpg.Connection,
    chunks: list[EmbeddedChunk],
) -> None:
    await conn.executemany(
        """
        INSERT INTO chunks (
            chunk_id, document_id, text, embedding,
            clause_label, page_number, char_start, char_end, token_count
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (chunk_id) DO UPDATE SET embedding = EXCLUDED.embedding
        """,
        [
            (
                chunk.chunk_id,
                chunk.document_id,
                chunk.text,
                str(chunk.embedding),
                chunk.clause_label,
                chunk.page_number,
                chunk.char_start,
                chunk.char_end,
                chunk.token_count,
            )
            for chunk in chunks
        ],
    )
