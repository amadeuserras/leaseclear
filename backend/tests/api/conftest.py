from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest
from fastapi.testclient import TestClient

from leaseclear.api.main import app
from leaseclear.core.config import settings
from leaseclear.db.connection import close_pool
from leaseclear.types import Citation, GenerationResult, LabelledChunk


@pytest.fixture
def mock_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate(question: str, chunks: list[LabelledChunk]) -> GenerationResult:
        if "daycare" in question.lower():
            return GenerationResult(
                answer="This is not specified in the provided lease(s).",
                citations=[],
                confidence=0.0,
                refusal=True,
            )

        deposit_chunk = next(
            (c for c in chunks if "deposit" in c.text.lower()),
            None,
        )
        if deposit_chunk is None:
            raise AssertionError("expected retrieval to return a deposit chunk")

        return GenerationResult(
            answer=f"The security deposit is $5,750.00. {deposit_chunk.citation_id}",
            citations=[
                Citation(id=deposit_chunk.citation_id, quote="$5,750.00"),
            ],
            confidence=1.0,
            refusal=False,
        )

    monkeypatch.setattr("leaseclear.api.query.generate", fake_generate)


@pytest.fixture
async def api_client(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
    seeded_db: asyncpg.Connection,
    mock_generate: None,
) -> AsyncIterator[TestClient]:
    monkeypatch.setattr(settings, "database_url", database_url)
    await close_pool()

    with TestClient(app) as client:
        yield client

    await close_pool()
