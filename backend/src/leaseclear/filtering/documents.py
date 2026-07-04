from __future__ import annotations

from uuid import UUID

from leaseclear.db.connection import get_conn
from leaseclear.types import DocumentMetadata


async def list_document_metadata(
    document_ids: list[UUID] | None = None,
) -> list[DocumentMetadata]:
    rows = await get_conn().fetch(
        """--sql
        SELECT id, slug, filename, landlord_name, tenant_names, property_address
        FROM documents
        WHERE ($1::uuid[] IS NULL OR id = ANY($1))
        """,
        document_ids,
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


async def list_owned_document_ids(user_id: UUID) -> list[UUID]:
    rows = await get_conn().fetch(
        "SELECT id FROM documents WHERE user_id = $1",
        user_id,
    )
    return [row["id"] for row in rows]
