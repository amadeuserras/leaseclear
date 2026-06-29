from __future__ import annotations

from leaseclear.db.connection import DbConnection
from leaseclear.types import AssignedDocument, EmbeddedChunk


async def store_documents(
    conn: DbConnection,
    documents: list[AssignedDocument],
) -> None:
    await conn.executemany(
        """--sql
        INSERT INTO documents (id, filename, slug)
        VALUES ($1, $2, $3)
        """,
        [(doc.id, doc.filename, doc.slug) for doc in documents],
    )


async def store_chunks(
    conn: DbConnection,
    chunks: list[EmbeddedChunk],
) -> None:
    await conn.executemany(
        """--sql
        INSERT INTO chunks (
            id, document_id, document_slug, text, embedding,
            clause_label, page_number, char_start, char_end, token_count
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding
        """,
        [
            (
                chunk.id,
                chunk.document_id,
                chunk.document_slug,
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
