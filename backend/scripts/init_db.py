from __future__ import annotations

import asyncio
import json
from pathlib import Path

import asyncpg

from leaseclear.core.config import settings
from leaseclear.db.connection import DbConnection, apply_schema
from leaseclear.ingestion.store import store_chunks, store_document
from leaseclear.types import EmbeddedChunk

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


async def seed_db(conn: DbConnection) -> None:
    await apply_schema(conn)
    await conn.execute("TRUNCATE chunks, logs, users, documents")
    for chunks_file in sorted(DATA_DIR.glob("*-chunks.json")):
        document_id = chunks_file.stem.removesuffix("-chunks")
        chunks = [EmbeddedChunk(**c) for c in json.loads(chunks_file.read_text())]
        filename = f"{document_id}.pdf"
        await store_document(conn, document_id, filename)
        await store_chunks(conn, chunks)
        print(f"Seeded {len(chunks)} chunks for {document_id}")


async def main() -> None:
    conn = await asyncpg.connect(settings.database_url)
    try:
        await seed_db(conn)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
