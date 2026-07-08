from __future__ import annotations

from uuid import UUID

from leaseclear.db.connection import get_conn
from leaseclear.types import ChunkBase, DocumentMetadata


async def get_chunks_by_documents(
    document_ids: list[UUID], per_document: int = 8
) -> list[ChunkBase]:
    """A random per-document sample of chunks from the given documents.

    Gives an LLM enough varied context to suggest questions without sending an
    entire corpus. Samples randomly per document (not overall) so every document
    is represented and the selection differs run to run. Not a retrieval path.
    """
    rows = await get_conn().fetch(
        """--sql
        SELECT id, document_id, document_slug, text, clause_number, clause_label,
               page_number, char_start, char_end, token_count
        FROM (
            SELECT *, row_number() OVER (
                PARTITION BY document_id ORDER BY random()
            ) AS rn
            FROM chunks
            WHERE document_id = ANY($1)
        ) ranked
        WHERE rn <= $2
        ORDER BY document_slug, char_start
        """,
        document_ids,
        per_document,
    )
    return [ChunkBase(**dict(row)) for row in rows]


async def get_documents(user_id: UUID) -> list[DocumentMetadata]:
    rows = await get_conn().fetch(
        """--sql
        SELECT id, slug, filename, landlord_name, tenant_names, property_address
        FROM documents
        WHERE user_id = $1
        ORDER BY created_at DESC
        """,
        user_id,
    )
    return [
        DocumentMetadata(
            id=row["id"],
            slug=row["slug"],
            filename=row["filename"],
            landlord_name=row["landlord_name"],
            tenant_names=row["tenant_names"] or [],
            property_address=row["property_address"],
        )
        for row in rows
    ]
