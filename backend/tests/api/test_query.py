from __future__ import annotations

from fastapi.testclient import TestClient


def test_query_returns_cited_answer(api_client: TestClient) -> None:
    response = api_client.post(
        "/query",
        json={"question": "How much is the security deposit?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] > 0.5
    assert data["citations"]
    assert any(
        "deposit" in citation["clause_label"].lower()
        or "deposit" in citation["passage"].lower()
        for citation in data["citations"]
    )


def test_query_refuses_unanswerable_question(api_client: TestClient) -> None:
    response = api_client.post(
        "/query",
        json={"question": "Can I operate a daycare from the unit?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] == 0.0
    assert data["citations"] == []
    assert "not specified" in data["answer"].lower()
