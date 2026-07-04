from __future__ import annotations

from uuid import UUID

from leaseclear.db.connection import db_session
from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.metadata import extract_metadata
from leaseclear.ingestion.parse import parse_document
from leaseclear.ingestion.store import store_chunks, store_documents
from leaseclear.types import ChunkBase, UploadDocument


async def ingest_documents(
    uploads: list[UploadDocument],
    user_id: UUID | None = None,
) -> list[ChunkBase]:
    parsed = [parse_document(upload) for upload in uploads]
    slugs: set[str] = set()
    assigned = [assign_document(doc, slugs) for doc in parsed]
    enriched = await extract_metadata(assigned)
    chunks = chunk_documents(enriched)
    embedded = embed_chunks(chunks)

    async with db_session() as conn, conn.transaction():
        await store_documents(enriched, user_id=user_id)
        await store_chunks(embedded)

    return chunks
