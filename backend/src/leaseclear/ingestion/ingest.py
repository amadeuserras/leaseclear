from __future__ import annotations

from leaseclear.db.connection import get_pool
from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_document
from leaseclear.ingestion.store import store_chunks, store_documents
from leaseclear.types import ChunkBase, UploadDocument


async def ingest_documents(uploads: list[UploadDocument]) -> list[ChunkBase]:
    parsed = [parse_document(upload) for upload in uploads]
    slugs: set[str] = set()
    assigned = [assign_document(doc, slugs) for doc in parsed]
    chunks = chunk_documents(assigned)
    embedded = embed_chunks(chunks)

    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        await store_documents(conn, assigned)
        await store_chunks(conn, embedded)

    return chunks
