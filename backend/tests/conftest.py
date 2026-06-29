from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path

import asyncpg
import pytest

from leaseclear.core.config import settings
from leaseclear.db.connection import apply_schema
from leaseclear.ingestion.store import store_chunks, store_document
from leaseclear.types import EmbeddedChunk

CORPUS_LEASE_PDF = Path(__file__).resolve().parent / "fixtures" / "test_lease.pdf"
CORPUS_LEASE_DOCUMENT_ID = "test_lease"

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "seed_corpus.json"
_fixture_data = json.loads(FIXTURE_PATH.read_text())
SEED_CHUNKS = [EmbeddedChunk(**c) for c in _fixture_data["chunks"]]
QUERY_EMBEDDINGS = _fixture_data["query_embeddings"]


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


@pytest.fixture(autouse=True)
def mock_embed_texts(
    request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch
) -> None:
    if request.node.get_closest_marker("real_api") is not None:
        return

    def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [QUERY_EMBEDDINGS[text] for text in texts]

    monkeypatch.setattr("leaseclear.retrieval.vector.embed_texts", fake_embed_texts)


@pytest.fixture
async def seeded_db(
    database_url: str,
    ensure_test_database: None,
) -> AsyncIterator[asyncpg.Connection]:
    conn = await asyncpg.connect(database_url)
    try:
        await apply_schema(conn)
        await conn.execute("TRUNCATE chunks, logs, users, documents")
        await store_document(conn, CORPUS_LEASE_DOCUMENT_ID, CORPUS_LEASE_PDF.name)
        await store_chunks(conn, SEED_CHUNKS)
        yield conn
    finally:
        await conn.execute("TRUNCATE chunks, logs, users, documents")
        await conn.close()
