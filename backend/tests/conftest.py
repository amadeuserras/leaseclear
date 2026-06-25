from __future__ import annotations

import random
from collections.abc import AsyncIterator

import asyncpg
import pytest

from leaseclear.core.config import settings
from scripts.init_db import seed_db


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
            "SELECT 1 FROM pg_database WHERE datname = $1", db_name
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


@pytest.fixture(autouse=True)
def mock_embed_texts(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    if request.node.get_closest_marker("real_api") is not None:
        return

    def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [[random.gauss(0, 1) for _ in range(1536)] for _ in texts]

    monkeypatch.setattr("leaseclear.retrieval.vector.embed_texts", fake_embed_texts)


@pytest.fixture
async def seeded_db(
    database_url: str,
    ensure_test_database: None,
) -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(database_url)
    try:
        await seed_db(conn)
        yield conn
    finally:
        await conn.close()
