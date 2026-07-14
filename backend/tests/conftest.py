from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import uuid4

import asyncpg
import pytest

from leaseclear.core.config import settings
from leaseclear.db.connection import _session_ctx, apply_schema
from leaseclear.db.create import ensure_database
from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.ingestion.store import store_chunks, store_documents
from leaseclear.types import ChunkBase, Citation, GenerationResult
from tests.data.corpus import SEED_CHUNKS, SEED_DOCUMENT

_FAKE_QUERY_EMBEDDING = [0.01] * 1536


@pytest.fixture(scope="session")
def database_url() -> str:
    return settings.test_database_url


@pytest.fixture(scope="session")
async def ensure_test_database(database_url: str) -> None:
    await ensure_database(database_url)


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


@pytest.fixture
def mock_embed_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "leaseclear.retrieval.vector.embed_texts",
        lambda texts: [_FAKE_QUERY_EMBEDDING for _ in texts],
    )


@pytest.fixture
def chunks() -> list[ChunkBase]:
    document_id = uuid4()
    return [
        ChunkBase(
            id=uuid4(),
            document_id=document_id,
            document_slug="lease",
            text="Tenant shall pay Rent of $2,875.00 per month.",
            clause_number="3",
            clause_title="Rent",
            start_page=1,
            end_page=1,
            index=0,
            citation="§3",
        ),
        ChunkBase(
            id=uuid4(),
            document_id=document_id,
            document_slug="lease",
            text="Tenant shall deposit $5,750.00 as a security deposit.",
            clause_number="4",
            clause_title="Security Deposit",
            start_page=1,
            end_page=1,
            index=1,
            citation="§4",
        ),
    ]


@pytest.fixture
def cited_result() -> GenerationResult:
    return GenerationResult(
        answer="The security deposit is $5,750.00. [lease §4]",
        citations=[Citation(id="[lease §4]")],
    )


@pytest.fixture
def refusal_result() -> GenerationResult:
    return GenerationResult(
        answer=REFUSAL_MESSAGE,
        citations=[],
    )
