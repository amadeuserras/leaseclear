from __future__ import annotations

from uuid import UUID

from leaseclear.db.connection import get_conn
from leaseclear.types import EmbeddedChunk, EnrichedDocument


async def store_documents(
    documents: list[EnrichedDocument],
    user_id: UUID | None = None,
) -> None:
    await get_conn().executemany(
        """--sql
        INSERT INTO documents (
            id, user_id, filename, slug, landlord_name, tenant_names,
            property_address
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        [
            (
                doc.id,
                user_id,
                doc.filename,
                doc.slug,
                doc.landlord_name,
                doc.tenant_names,
                doc.property_address,
            )
            for doc in documents
        ],
    )


async def store_chunks(chunks: list[EmbeddedChunk]) -> None:
    await get_conn().executemany(
        """--sql
        INSERT INTO chunks (
            id, document_id, document_slug, text, embedding,
            clause_number, clause_label, page_number, char_start, char_end, token_count
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
        ON CONFLICT (id) DO UPDATE SET embedding = EXCLUDED.embedding
        """,
        [
            (
                chunk.id,
                chunk.document_id,
                chunk.document_slug,
                chunk.text,
                str(chunk.embedding),
                chunk.clause_number,
                chunk.clause_label,
                chunk.page_number,
                chunk.char_start,
                chunk.char_end,
                chunk.token_count,
            )
            for chunk in chunks
        ],
    )
