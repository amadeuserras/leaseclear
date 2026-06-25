from __future__ import annotations

from leaseclear.db.connection import DbConnection
from leaseclear.types import EmbeddedChunk


async def store_document(
    conn: DbConnection,
    document_id: str,
    filename: str,
) -> None:
    await conn.execute(
        """--sql
        INSERT INTO documents (id, filename)
        VALUES ($1, $2)
        """,
        document_id,
        filename,
    )


async def store_chunks(
    conn: DbConnection,
    chunks: list[EmbeddedChunk],
) -> None:
    await conn.executemany(
        """--sql
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
