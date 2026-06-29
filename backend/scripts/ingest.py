import asyncio
from pathlib import Path

from leaseclear.db.connection import apply_schema, close_pool, get_pool
from leaseclear.ingestion.ingest import ingest_documents
from leaseclear.types import UploadDocument

DEFAULT_PDF = (
    Path(__file__).resolve().parents[2]
    / "corpus"
    / "generated"
    / "meridian-nadkarni_osei.pdf"
)


async def main() -> None:
    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            await apply_schema(conn)
            await conn.execute("TRUNCATE chunks, documents")
            chunks = await ingest_documents(
                [UploadDocument(path=str(DEFAULT_PDF), filename=DEFAULT_PDF.name)]
            )
            print(f"Ingested {len(chunks)} chunks from {DEFAULT_PDF}")
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
