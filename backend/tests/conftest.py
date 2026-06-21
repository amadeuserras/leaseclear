from __future__ import annotations

import asyncpg
import pytest

from leaseclear.core.config import settings


async def _ensure_test_database(database_url: str) -> None:
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


@pytest.fixture(scope="session")
async def ensure_test_database(database_url: str) -> None:
    await _ensure_test_database(database_url)


@pytest.fixture(scope="session")
def database_url() -> str:
    return settings.test_database_url
