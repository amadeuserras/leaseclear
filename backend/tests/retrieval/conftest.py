from __future__ import annotations

import pytest

_FAKE_QUERY_EMBEDDING = [0.01] * 1536


@pytest.fixture(autouse=True)
def mock_embed_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "leaseclear.retrieval.vector.embed_texts",
        lambda texts: [_FAKE_QUERY_EMBEDDING for _ in texts],
    )
