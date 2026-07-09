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


async def get_document_chunks(slug: str, user_id: UUID) -> list[ChunkBase]:
    """Every chunk of the user's document with the given slug, in reading order.

    Powers the document viewer, which shows the whole document rather than only
    the chunks a query cited. Joins through `documents` so the slug is scoped to
    the requesting user.
    """
    rows = await get_conn().fetch(
        """--sql
        SELECT c.id, c.document_id, c.document_slug, c.text, c.clause_number,
               c.clause_label, c.page_number, c.char_start, c.char_end,
               c.token_count
        FROM chunks c
        JOIN documents d ON d.id = c.document_id
        WHERE d.user_id = $1 AND c.document_slug = $2
        ORDER BY c.page_number, c.char_start
        """,
        user_id,
        slug,
    )
    return [ChunkBase(**dict(row)) for row in rows]


async def delete_document(document_id: UUID, user_id: UUID) -> bool:
    """Delete a user's document (chunks cascade). False if it wasn't theirs."""
    result = await get_conn().execute(
        """--sql
        DELETE FROM documents WHERE id = $1 AND user_id = $2
        """,
        document_id,
        user_id,
    )
    return result != "DELETE 0"


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
