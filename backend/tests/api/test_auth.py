from __future__ import annotations

import jwt
from fastapi.testclient import TestClient

from leaseclear.core.config import settings


def test_register_returns_bearer_token(api_client: TestClient) -> None:
    response = api_client.post(
        "/auth/register",
        json={"email": "a@b.com", "password": "hunter2"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    payload = jwt.decode(
        body["access_token"],
        settings.jwt_secret,
        algorithms=["HS256"],
    )
    assert payload["sub"]


def test_register_duplicate_email_returns_409(api_client: TestClient) -> None:
    creds = {"email": "dup@b.com", "password": "hunter2"}
    assert api_client.post("/auth/register", json=creds).status_code == 200
    assert api_client.post("/auth/register", json=creds).status_code == 409


def test_login_returns_token_for_valid_credentials(api_client: TestClient) -> None:
    creds = {"email": "login@b.com", "password": "hunter2"}
    api_client.post("/auth/register", json=creds)

    response = api_client.post("/auth/login", json=creds)
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_returns_401_for_wrong_password(api_client: TestClient) -> None:
    api_client.post(
        "/auth/register",
        json={"email": "wrongpw@b.com", "password": "hunter2"},
    )

    response = api_client.post(
        "/auth/login",
        json={"email": "wrongpw@b.com", "password": "wrong"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_returns_401_for_unknown_email(api_client: TestClient) -> None:
    response = api_client.post(
        "/auth/login",
        json={"email": "nobody@b.com", "password": "hunter2"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_documents_requires_auth(api_client: TestClient) -> None:
    response = api_client.post("/documents")
    assert response.status_code == 401


def test_documents_rejects_bad_token(api_client: TestClient) -> None:
    response = api_client.post(
        "/documents", headers={"Authorization": "Bearer garbage"}
    )
    assert response.status_code == 401


def test_documents_accepts_valid_token(
    api_client: TestClient,
    mock_upload_document: None,
) -> None:
    response = api_client.post(
        "/auth/register",
        json={"email": "upload@b.com", "password": "hunter2"},
    )

    assert response.status_code == 200
    valid_token = response.json()["access_token"]

    response = api_client.post(
        "/documents",
        headers={"Authorization": f"Bearer {valid_token}"},
        files={"file": ("lease.pdf", b"fake-pdf", "application/pdf")},
    )
    assert response.status_code == 200


def test_query_does_not_require_auth(
    api_client: TestClient, mock_generate_stream: None
) -> None:
    with api_client.stream(
        "POST",
        "/query",
        json={"question": "How much is the security deposit?"},
    ) as response:
        assert response.status_code == 200
