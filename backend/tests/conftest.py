from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest

from leaseclear.core.config import settings
from tests.db import ensure_database_exists, reset_and_seed_lease, truncate_chunks


@pytest.fixture(scope="session")
def database_url() -> str:
    return settings.test_database_url


@pytest.fixture(scope="session")
async def ensure_test_database(database_url: str) -> None:
    await ensure_database_exists(database_url)


@pytest.fixture
async def seeded_db(
    database_url: str,
    ensure_test_database: None,
) -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(database_url)
    try:
        await reset_and_seed_lease(conn)
        yield conn
    finally:
        await truncate_chunks(conn)
        await conn.close()
