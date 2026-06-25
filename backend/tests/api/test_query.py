from __future__ import annotations

import json
import re
from collections.abc import AsyncIterator

import pytest
from fastapi.testclient import TestClient

from leaseclear.generation.prompts import DELIMITER
from leaseclear.types import LabelledChunk


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


@pytest.fixture
def mock_generate_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_generate_stream(
        question: str, chunks: list[LabelledChunk]
    ) -> AsyncIterator[str]:
        cid = chunks[0].citation_id if chunks else "[lease §unknown]"
        for token in (
            "A mock answer. ",
            cid,
            "\n",
            DELIMITER,
            "\n",
            f'{{"citations": [{{"id": "{cid}", "quote": "mock passage"}}], "confidence": 0.9}}',
        ):
            yield token

    monkeypatch.setattr("leaseclear.api.query.generate_stream", fake_generate_stream)


def test_query_endpoint_streams_sse(
    api_client: TestClient, mock_generate_stream: None
) -> None:
    with api_client.stream(
        "POST",
        "/query",
        json={"question": "How much is the security deposit?"},
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
    assert payload["confidence"] == 0.9
    assert len(payload["citations"]) == 1
    assert payload["citations"][0]["passage"] == "mock passage"
