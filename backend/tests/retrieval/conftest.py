from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import pytest

from leaseclear.db.connection import apply_schema
from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_pdf
from leaseclear.ingestion.store import store_chunks

LEASE_PDF = Path(__file__).resolve().parents[3] / "corpus" / "generated" / "lease.pdf"


@pytest.fixture(scope="session")
async def seeded_db(
    ensure_test_database: None,
    database_url: str,
) -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(database_url)
    try:
        await apply_schema(conn)
        await conn.execute("TRUNCATE chunks")
        document = parse_pdf(LEASE_PDF)
        chunks = chunk_document(document, "lease")
        embedded = embed_chunks(chunks)
        await store_chunks(conn, embedded)
        yield conn
    finally:
        await conn.close()
