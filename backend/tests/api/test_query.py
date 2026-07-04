from __future__ import annotations

import json
import re
from uuid import UUID

import asyncpg
from fastapi.testclient import TestClient

from leaseclear.generation.prompts import DELIMITER
from tests.api.conftest import MOCK_INPUT_TOKENS, MOCK_OUTPUT_TOKENS
from tests.data.corpus import CORPUS_LEASE_DOCUMENT_ID


def parse_sse_events(body: str) -> list[tuple[str, str]]:
    events: list[tuple[str, str]] = []
    for block in re.split(r"\r?\n\r?\n", body.strip()):
        if not block.strip() or block.startswith(":"):
            continue
        event_type = ""
        data = ""
        for line in block.splitlines():
            if line.startswith("event:"):
                event_type = line.removeprefix("event:").strip()
            elif line.startswith("data:"):
                data = line.removeprefix("data:").strip()
        if event_type or data:
            events.append((event_type, data))
    return events


def test_query_endpoint_streams_sse(
    api_client: TestClient,
    mock_generate_stream: None,
    owner: tuple[dict[str, str], UUID],
    owned_seed: None,
) -> None:
    headers, _ = owner
    with api_client.stream(
        "POST",
        "/query",
        json={"question": "How much is the security deposit?"},
        headers=headers,
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")
        body = response.read().decode()

    events = parse_sse_events(body)
    token_events = [(event, data) for event, data in events if event == "token"]
    done_events = [(event, data) for event, data in events if event == "done"]

    assert token_events
    assert len(done_events) == 1
    streamed = "".join(data for _, data in token_events)
    assert streamed.startswith("A mock answer.")
    assert DELIMITER not in streamed

    payload = json.loads(done_events[0][1])
    assert isinstance(payload["answer"], str)
    assert payload["citations"], "owned document should be retrieved and cited"


def test_query_only_searches_own_documents(
    api_client: TestClient,
    mock_generate_stream: None,
    owned_seed: None,
) -> None:
    response = api_client.post(
        "/auth/register",
        json={"email": "stranger@test.com", "password": "hunter2"},
    )
    headers = {"Authorization": f"Bearer {response.json()['access_token']}"}

    with api_client.stream(
        "POST",
        "/query",
        json={
            "question": "How much is the security deposit?",
            "document_ids": [str(CORPUS_LEASE_DOCUMENT_ID)],
        },
        headers=headers,
    ) as response:
        assert response.status_code == 200
        body = response.read().decode()

    done_data = next(data for event, data in parse_sse_events(body) if event == "done")
    assert json.loads(done_data)["citations"] == []


async def test_query_writes_log_row(
    api_client: TestClient,
    seed_db: asyncpg.Connection,
    mock_generate_stream: None,
    owner: tuple[dict[str, str], UUID],
    owned_seed: None,
) -> None:
    headers, user_id = owner
    question = "How much is the security deposit?"

    with api_client.stream(
        "POST",
        "/query",
        json={"question": question},
        headers=headers,
    ) as response:
        assert response.status_code == 200
        response.read()

    row = await seed_db.fetchrow(
        "SELECT * FROM logs WHERE question = $1",
        question,
    )
    assert row is not None
    assert row["user_id"] == user_id
    assert row["document_ids"] is None
    assert isinstance(row["chunk_ids_retrieved"], list)
    assert row["chunk_ids_retrieved"]
    assert row["input_tokens"] == MOCK_INPUT_TOKENS
    assert row["output_tokens"] == MOCK_OUTPUT_TOKENS
    assert row["refused"] is False
    assert row["ttft_s"] is not None and row["ttft_s"] > 0
    assert row["total_s"] is not None and row["total_s"] >= row["ttft_s"]
