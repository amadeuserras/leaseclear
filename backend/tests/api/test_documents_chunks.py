from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient


def test_get_chunks_requires_auth(api_client: TestClient) -> None:
    assert api_client.get("/documents/test-lease/chunks").status_code == 401


def test_get_chunks_returns_full_document_in_reading_order(
    api_client: TestClient,
    owner: tuple[dict[str, str], UUID],
    owned_seed: None,
) -> None:
    headers, _ = owner
    response = api_client.get("/documents/test-lease/chunks", headers=headers)
    assert response.status_code == 200
    chunks = response.json()
    assert len(chunks) == 24

    first = chunks[0]
    assert set(first) == {
        "chunk_id",
        "clause_number",
        "clause_title",
        "start_page",
        "end_page",
        "index",
        "citation",
        "passage",
    }

    ordering = [c["index"] for c in chunks]
    assert ordering == sorted(ordering)


def test_get_chunks_unknown_slug_returns_404(
    api_client: TestClient,
    owner: tuple[dict[str, str], UUID],
    owned_seed: None,
) -> None:
    headers, _ = owner
    response = api_client.get("/documents/does-not-exist/chunks", headers=headers)
    assert response.status_code == 404


def test_get_chunks_excludes_other_users_documents(
    api_client: TestClient,
    owned_seed: None,
) -> None:
    other = api_client.post(
        "/auth/register",
        json={"email": "other@test.com", "password": "hunter2"},
    )
    token = other.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = api_client.get("/documents/test-lease/chunks", headers=headers)
    assert response.status_code == 404
