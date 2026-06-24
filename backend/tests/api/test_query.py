from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from leaseclear.types import Citation, GenerationResult, LabelledChunk


@pytest.fixture
def mock_generate(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate(question: str, chunks: list[LabelledChunk]) -> GenerationResult:
        citations = (
            [Citation(id=chunks[0].citation_id, quote="mock passage")] if chunks else []
        )
        return GenerationResult(
            answer="A mock answer.",
            citations=citations,
            confidence=0.9,
        )

    monkeypatch.setattr("leaseclear.api.query.generate", fake_generate)


def test_query_endpoint_shape(api_client: TestClient) -> None:
    response = api_client.post(
        "/query",
        json={"question": "How much is the security deposit?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "A mock answer."
    assert data["confidence"] == 0.9
    assert len(data["citations"]) == 1

    citation = data["citations"][0]
    assert citation["passage"] == "mock passage"
    assert citation["chunk_id"]
    assert isinstance(citation["clause_label"], str)
    assert isinstance(citation["page_number"], int)
