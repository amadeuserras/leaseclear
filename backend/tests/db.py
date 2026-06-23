from __future__ import annotations

from pathlib import Path

import asyncpg

from leaseclear.db.connection import DbConnection, apply_schema
from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_pdf
from leaseclear.ingestion.store import store_chunks

REPO_ROOT = Path(__file__).resolve().parents[2]
LEASE_PDF = REPO_ROOT / "corpus" / "generated" / "lease.pdf"
LEASE_DOCUMENT_ID = "lease"


async def ensure_database_exists(database_url: str) -> None:
    db_name = database_url.rsplit("/", 1)[-1]
    admin_url = f"{database_url.rsplit('/', 1)[0]}/postgres"
    conn = await asyncpg.connect(admin_url)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name,
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


async def truncate_chunks(conn: DbConnection) -> None:
    await conn.execute("TRUNCATE chunks")


async def reset_and_seed_lease(conn: DbConnection) -> int:
    await apply_schema(conn)
    await truncate_chunks(conn)
    document = parse_pdf(LEASE_PDF)
    chunks = chunk_document(document, LEASE_DOCUMENT_ID)
    embedded = embed_chunks(chunks)
    await store_chunks(conn, embedded)
    return len(embedded)
