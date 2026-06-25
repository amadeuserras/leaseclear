from __future__ import annotations

import random
from collections.abc import AsyncIterator

import asyncpg
import pytest

from leaseclear.core.config import settings
from scripts.init_db import seed_db
from tests.db import ensure_database_exists, truncate_db


@pytest.fixture(scope="session")
def database_url() -> str:
    return settings.test_database_url


@pytest.fixture(scope="session")
async def ensure_test_database(database_url: str) -> None:
    await ensure_database_exists(database_url)


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
        await truncate_db(conn)
        await conn.close()
