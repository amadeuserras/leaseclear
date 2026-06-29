import asyncio
from pathlib import Path

from leaseclear.db.connection import apply_schema, close_pool, get_pool
from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_pdf
from leaseclear.ingestion.store import store_chunks, store_document

DEFAULT_PDF = (
    Path(__file__).resolve().parents[2]
    / "corpus"
    / "generated"
    / "meridian-nadkarni_osei.pdf"
)
DEFAULT_DOCUMENT_ID = "00000000-0000-0000-0000-000000000001"


async def main() -> None:
    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            await apply_schema(conn)
            await conn.execute("TRUNCATE chunks, documents")
            document = parse_pdf(DEFAULT_PDF)
            chunks = chunk_document(document, DEFAULT_DOCUMENT_ID)
            embedded = embed_chunks(chunks)
            await store_document(conn, DEFAULT_DOCUMENT_ID, DEFAULT_PDF.name)
            await store_chunks(conn, embedded)
            print(f"Ingested {len(embedded)} chunks from {DEFAULT_PDF}")
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
