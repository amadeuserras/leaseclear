from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest

from leaseclear.core.config import settings
from tests.corpus_fixture import load_query_embeddings
from tests.db import ensure_database_exists, reset_and_seed_lease, truncate_db


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

    query_embeddings = load_query_embeddings()

    def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [query_embeddings[text] for text in texts]

    monkeypatch.setattr("leaseclear.retrieval.vector.embed_texts", fake_embed_texts)


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
        await truncate_db(conn)
        await conn.close()
