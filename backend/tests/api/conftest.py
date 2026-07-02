from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest
from fastapi.testclient import TestClient

from leaseclear.api.limiter import limiter
from leaseclear.api.main import app
from leaseclear.core.config import settings
from leaseclear.db.connection import close_pool
from leaseclear.generation.prompts import DELIMITER
from leaseclear.types import ChunkBase, GenerationStreamMeta

MOCK_INPUT_TOKENS = 10
MOCK_OUTPUT_TOKENS = 20
_FAKE_QUERY_EMBEDDING = [0.01] * 1536


@pytest.fixture(autouse=True)
def mock_embed_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_embed_texts(texts: list[str]) -> list[list[float]]:
        return [_FAKE_QUERY_EMBEDDING for _ in texts]

    monkeypatch.setattr("leaseclear.retrieval.vector.embed_texts", fake_embed_texts)


@pytest.fixture
def mock_generate_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate_stream(
        question: str, chunks: list[ChunkBase]
    ) -> tuple[AsyncIterator[str], GenerationStreamMeta]:
        async def tokens() -> AsyncIterator[str]:
            cid = chunks[0].citation_id if chunks else "[lease §unknown]"
            yield (
                f"A mock answer. {cid}\n{DELIMITER}\n"
                f'["{cid}"]'
            )

        return tokens(), GenerationStreamMeta(
            input_tokens=MOCK_INPUT_TOKENS,
            output_tokens=MOCK_OUTPUT_TOKENS,
        )

    monkeypatch.setattr("leaseclear.api.query.generate_stream", fake_generate_stream)


@pytest.fixture
def mock_upload_document(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_upload_documents(_files: object) -> None:
        return None

    monkeypatch.setattr("leaseclear.api.main.upload_documents", fake_upload_documents)


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    limiter.reset()


@pytest.fixture
async def api_client(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
    seed_db: asyncpg.Connection,
) -> AsyncIterator[TestClient]:
    monkeypatch.setattr(settings, "database_url", database_url)
    monkeypatch.setattr(
        settings, "jwt_secret", "test-jwt-secret-for-leaseclear-tests-only"
    )
    await close_pool()

    with TestClient(app) as client:
        yield client

    await close_pool()
