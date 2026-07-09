from __future__ import annotations

from uuid import UUID, uuid4

from fastapi.testclient import TestClient

from tests.data.corpus import CORPUS_LEASE_DOCUMENT_ID


def test_delete_requires_auth(api_client: TestClient) -> None:
    assert api_client.delete(f"/documents/{uuid4()}").status_code == 401


def test_delete_removes_document_and_chunks(
    api_client: TestClient,
    owner: tuple[dict[str, str], UUID],
    owned_seed: None,
) -> None:
    headers, _ = owner

    response = api_client.delete(
        f"/documents/{CORPUS_LEASE_DOCUMENT_ID}", headers=headers
    )
    assert response.status_code == 204

    assert api_client.get("/documents", headers=headers).json() == []
    assert (
        api_client.get("/documents/test-lease/chunks", headers=headers).status_code
        == 404
    )


def test_delete_unknown_document_returns_404(
    api_client: TestClient,
    owner: tuple[dict[str, str], UUID],
) -> None:
    headers, _ = owner
    response = api_client.delete(f"/documents/{uuid4()}", headers=headers)
    assert response.status_code == 404


def test_delete_other_users_document_returns_404(
    api_client: TestClient,
    owned_seed: None,
) -> None:
    other = api_client.post(
        "/auth/register",
        json={"email": "other@test.com", "password": "hunter2"},
    )
    token = other.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = api_client.delete(
        f"/documents/{CORPUS_LEASE_DOCUMENT_ID}", headers=headers
    )
    assert response.status_code == 404
