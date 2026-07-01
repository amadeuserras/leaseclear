from __future__ import annotations

from leaseclear.db.connection import get_conn
from leaseclear.types import DocumentMetadata


async def list_document_metadata() -> list[DocumentMetadata]:
    rows = await get_conn().fetch(
        """--sql
        SELECT id, landlord_name, tenant_names, property_address
        FROM documents
        """
    )
    return [
        DocumentMetadata(
            id=row["id"],
            landlord_name=row["landlord_name"],
            tenant_names=row["tenant_names"] or [],
            property_address=row["property_address"],
        )
        for row in rows
    ]
