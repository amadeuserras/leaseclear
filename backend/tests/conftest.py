from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest

from leaseclear.core.config import settings
from leaseclear.db.connection import _session_ctx, apply_schema
from leaseclear.ingestion.store import store_chunks, store_documents
from tests.data.corpus import SEED_CHUNKS, SEED_DOCUMENT


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
    token = _session_ctx.set(conn)
    try:
        await apply_schema()
        await conn.execute("TRUNCATE chunks, logs, users, documents")
        await store_documents([SEED_DOCUMENT])
        await store_chunks(SEED_CHUNKS)
        yield conn
    finally:
        _session_ctx.reset(token)
        await conn.execute("TRUNCATE chunks, logs, users, documents")
        await conn.close()
