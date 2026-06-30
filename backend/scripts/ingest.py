import asyncio
from pathlib import Path

from leaseclear.db.connection import apply_schema, close_pool, get_pool
from leaseclear.ingestion.ingest import ingest_documents
from leaseclear.types import UploadDocument

GENERATED_DIR = Path(__file__).resolve().parents[2] / "corpus" / "generated"


def discover_pdfs() -> list[Path]:
    return sorted(GENERATED_DIR.glob("*.pdf"))


async def main() -> None:
    pdfs = discover_pdfs()
    if not pdfs:
        raise SystemExit(
            f"No PDFs found in {GENERATED_DIR}. "
            "Run `uv run python generate.py` from corpus/ first."
        )

    uploads = [UploadDocument(path=str(pdf), filename=pdf.name) for pdf in pdfs]

    pool = await get_pool()
    try:
        async with pool.acquire() as conn:
            await apply_schema(conn)
            await conn.execute("TRUNCATE logs, chunks, documents")
            chunks = await ingest_documents(uploads)
            print(
                f"Ingested {len(chunks)} chunks from {len(pdfs)} PDFs "
                f"in {GENERATED_DIR}"
            )
            for pdf in pdfs:
                print(f"  - {pdf.name}")
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
