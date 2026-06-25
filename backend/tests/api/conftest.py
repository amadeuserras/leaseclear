from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest
from fastapi.testclient import TestClient

from leaseclear.api.main import app
from leaseclear.core.config import settings
from leaseclear.db.connection import close_pool
from leaseclear.generation.prompts import DELIMITER
from leaseclear.types import GenerationStreamMeta, LabelledChunk

MOCK_INPUT_TOKENS = 10
MOCK_OUTPUT_TOKENS = 20


@pytest.fixture
def mock_generate_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate_stream(
        question: str, chunks: list[LabelledChunk]
    ) -> tuple[AsyncIterator[str], GenerationStreamMeta]:
        async def tokens() -> AsyncIterator[str]:
            cid = chunks[0].citation_id if chunks else "[lease §unknown]"
            yield (
                f"A mock answer. {cid}\n{DELIMITER}\n"
                f'{{"citations": [{{"id": "{cid}", "quote": "mock passage"}}], "confidence": 0.9}}'
            )

        return tokens(), GenerationStreamMeta(
            input_tokens=MOCK_INPUT_TOKENS,
            output_tokens=MOCK_OUTPUT_TOKENS,
        )

    monkeypatch.setattr("leaseclear.api.query.generate_stream", fake_generate_stream)


@pytest.fixture
async def api_client(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
    seeded_db: asyncpg.Connection,
) -> AsyncIterator[TestClient]:
    monkeypatch.setattr(settings, "database_url", database_url)
    monkeypatch.setattr(
        settings, "jwt_secret", "test-jwt-secret-for-leaseclear-tests-only"
    )
    await close_pool()

    with TestClient(app) as client:
        yield client

    await close_pool()
