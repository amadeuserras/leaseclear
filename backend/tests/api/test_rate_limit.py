from __future__ import annotations

from fastapi.testclient import TestClient


def test_query_returns_429_after_limit(
    api_client: TestClient, mock_generate_stream: None
) -> None:
    payload = {"question": "How much is the security deposit?"}

    for _ in range(10):
        with api_client.stream("POST", "/query", json=payload) as response:
            assert response.status_code == 200
            response.read()

    response = api_client.post("/query", json=payload)
    assert response.status_code == 429


def test_documents_returns_429_after_limit(
    api_client: TestClient,
    mock_upload_document: None,
) -> None:
    register = api_client.post(
        "/auth/register",
        json={"email": "ratelimit@b.com", "password": "hunter2"},
    )
    token = register.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    files = {"files": ("lease.pdf", b"fake-pdf", "application/pdf")}

    for _ in range(5):
        response = api_client.post("/documents", headers=headers, files=files)
        assert response.status_code == 204

    response = api_client.post("/documents", headers=headers, files=files)
    assert response.status_code == 429


def test_login_returns_429_after_limit(api_client: TestClient) -> None:
    creds = {"email": "loginlimit@b.com", "password": "hunter2"}
    api_client.post("/auth/register", json=creds)

    for _ in range(5):
        response = api_client.post("/auth/login", json=creds)
        assert response.status_code == 200

    response = api_client.post("/auth/login", json=creds)
    assert response.status_code == 429
