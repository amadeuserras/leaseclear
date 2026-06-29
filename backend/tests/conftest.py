from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest

from leaseclear.core.config import settings
from leaseclear.db.connection import apply_schema
from leaseclear.ingestion.slug import make_document_slug
from leaseclear.ingestion.store import store_chunks, store_documents
from leaseclear.types import AssignedDocument
from tests.data.corpus import (
    CORPUS_LEASE_DOCUMENT_ID,
    CORPUS_LEASE_PDF,
    SEED_CHUNKS,
)


@pytest.fixture(scope="session")
def database_url() -> str:
    return settings.test_database_url


@pytest.fixture(scope="session")
async def ensure_test_database(database_url: str) -> None:
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


@pytest.fixture
async def seed_db(
    database_url: str,
    ensure_test_database: None,
) -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(database_url)
    try:
        await apply_schema(conn)
        await conn.execute("TRUNCATE chunks, logs, users, documents")
        await store_documents(
            conn,
            [
                AssignedDocument(
                    id=CORPUS_LEASE_DOCUMENT_ID,
                    slug=make_document_slug(CORPUS_LEASE_PDF.name),
                    filename=CORPUS_LEASE_PDF.name,
                    pages=[],
                )
            ],
        )
        await store_chunks(conn, SEED_CHUNKS)
        yield conn
    finally:
        await conn.execute("TRUNCATE chunks, logs, users, documents")
        await conn.close()
