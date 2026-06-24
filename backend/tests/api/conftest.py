from __future__ import annotations

from collections.abc import AsyncIterator

import asyncpg
import pytest
from fastapi.testclient import TestClient

from leaseclear.api.main import app
from leaseclear.core.config import settings
from leaseclear.db.connection import close_pool


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
