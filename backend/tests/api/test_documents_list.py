from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient


def test_get_documents_requires_auth(api_client: TestClient) -> None:
    assert api_client.get("/documents").status_code == 401


def test_get_documents_returns_empty_when_user_has_no_documents(
    api_client: TestClient,
    owner: tuple[dict[str, str], UUID],
) -> None:
    headers, _ = owner
    response = api_client.get("/documents", headers=headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_documents_returns_owned_documents(
    api_client: TestClient,
    owner: tuple[dict[str, str], UUID],
    owned_seed: None,
) -> None:
    headers, _ = owner
    response = api_client.get("/documents", headers=headers)
    assert response.status_code == 200
    docs = response.json()
    assert len(docs) == 1
    doc = docs[0]
    assert doc["filename"] == "test_lease.pdf"
    assert doc["landlord_name"] == "Cedar Grove Rentals LLC"
    assert "Priya Nadkarni" in doc["tenant_names"]
    assert "id" in doc and "slug" in doc


def test_get_documents_excludes_other_users_documents(
    api_client: TestClient,
    owned_seed: None,
) -> None:
    other = api_client.post(
        "/auth/register",
        json={"email": "other@test.com", "password": "hunter2"},
    )
    token = other.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = api_client.get("/documents", headers=headers)
    assert response.status_code == 200
    assert response.json() == []
