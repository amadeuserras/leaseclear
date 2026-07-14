from __future__ import annotations

from collections.abc import AsyncIterator
from uuid import UUID

import asyncpg
import jwt
import pytest
from fastapi.testclient import TestClient

from leaseclear.api.limiter import limiter
from leaseclear.api.main import app
from leaseclear.core.config import settings
from leaseclear.db.connection import use_database
from leaseclear.types import ChunkBase, DocumentMetadata, GenerationStreamMeta

MOCK_INPUT_TOKENS = 10
MOCK_OUTPUT_TOKENS = 20
_FAKE_QUERY_EMBEDDING = [0.01] * 1536


@pytest.fixture(autouse=True)
def mock_embed_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [_FAKE_QUERY_EMBEDDING for _ in texts]

    monkeypatch.setattr("leaseclear.retrieval.vector.embed_texts", fake_embed_texts)


@pytest.fixture(autouse=True)
def mock_filter_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_filter_documents(
        question: str, documents: list[DocumentMetadata]
    ) -> list[UUID]:
        return [d.id for d in documents]

    monkeypatch.setattr("leaseclear.api.query.filter_documents", fake_filter_documents)


@pytest.fixture
def mock_generate_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate_stream(
        question: str, chunks: list[ChunkBase], documents: list[DocumentMetadata]
    ) -> tuple[AsyncIterator[str], GenerationStreamMeta]:
        async def tokens() -> AsyncIterator[str]:
            cid = chunks[0].citation_id if chunks else "[lease §unknown]"
            yield f"A mock answer. {cid}"

        return tokens(), GenerationStreamMeta(
            input_tokens=MOCK_INPUT_TOKENS,
            output_tokens=MOCK_OUTPUT_TOKENS,
        )

    monkeypatch.setattr("leaseclear.api.query.generate_stream", fake_generate_stream)


@pytest.fixture
def mock_upload_document(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_upload_documents(_files: object, _user_id: object) -> None:
        return None

    monkeypatch.setattr("leaseclear.api.main.upload_documents", fake_upload_documents)


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    limiter.reset()


@pytest.fixture
def owner(api_client: TestClient) -> tuple[dict[str, str], UUID]:
    """A registered user: (auth headers, user id)."""
    response = api_client.post(
        "/auth/register",
        json={"email": "owner@test.com", "password": "hunter2"},
    )
    token = response.json()["access_token"]
    sub = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])["sub"]
    return {"Authorization": f"Bearer {token}"}, UUID(sub)


@pytest.fixture
async def owned_seed(
    owner: tuple[dict[str, str], UUID], seed_db: asyncpg.Connection
) -> None:
    """Assign the seeded document to the `owner` user."""
    _, user_id = owner
    await seed_db.execute("UPDATE documents SET user_id = $1", user_id)


@pytest.fixture
async def api_client(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
    seed_db: asyncpg.Connection,
) -> AsyncIterator[TestClient]:
    monkeypatch.setattr(
        settings, "jwt_secret", "test-jwt-secret-for-leaseclear-tests-only"
    )

    async with use_database(database_url):
        with TestClient(app) as client:
            yield client
