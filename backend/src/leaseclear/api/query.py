from __future__ import annotations

import json
import logging
import time
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

from leaseclear.api.schemas import Citation, QueryResponse
from leaseclear.db.connection import get_pool
from leaseclear.db.logs import insert_query_log
from leaseclear.generation.generate import generate_stream
from leaseclear.generation.label import label_chunks
from leaseclear.generation.prompts import DELIMITER, REFUSAL_MESSAGE
from leaseclear.generation.validate import validate
from leaseclear.retrieval import hybrid
from leaseclear.types import (
    ChunkBase,
    GenerationResult,
    LabelledChunk,
    QueryLogEntry,
)
from leaseclear.types import (
    Citation as GenCitation,
)

logger = logging.getLogger(__name__)


def _strip_markdown_fence(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned.startswith("```"):
        return cleaned
    cleaned = cleaned.split("\n", 1)[1]
    cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()


def _parse_metadata(raw: str) -> tuple[list[GenCitation], float]:
    parts = raw.split(DELIMITER, 1)
    if len(parts) != 2:
        raise ValueError(
            f"Expected prose and metadata separated by {DELIMITER!r}\n\nRaw:\n{raw}"
        )
    try:
        data = json.loads(_strip_markdown_fence(parts[1]))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude returned invalid metadata JSON: {e}\n\nRaw:\n{raw}"
        ) from e
    citations = [GenCitation(**c) for c in data.get("citations", [])]
    return citations, float(data["confidence"])


def _to_response(
    result: GenerationResult,
    retrieved: list[ChunkBase],
    labelled: list[LabelledChunk],
) -> QueryResponse:
    chunk_by_citation = {
        label.citation_id: chunk
        for label, chunk in zip(labelled, retrieved, strict=True)
    }
    citations = [
        Citation(
            chunk_id=chunk.chunk_id,
            clause_label=chunk.clause_label or "",
            page_number=chunk.page_number,
            passage=c.quote,
        )
        for c in result.citations
        if (chunk := chunk_by_citation.get(c.id)) is not None
    ]
    return QueryResponse(
        answer=result.answer,
        citations=citations,
        confidence=result.confidence,
    )


def _finalize(
    raw: str,
    labelled: list[LabelledChunk],
) -> GenerationResult:
    citations, confidence = _parse_metadata(raw)
    result = GenerationResult(answer="", citations=citations, confidence=confidence)
    validate(result, labelled, REFUSAL_MESSAGE)
    return result


async def _stream_prose(
    tokens: AsyncIterator[str], sink: list[str]
) -> AsyncIterator[str]:
    buffer = ""
    emitted = 0
    past_delimiter = False

    async for token in tokens:
        sink.append(token)
        if past_delimiter:
            continue

        buffer += token
        cut = buffer.find(DELIMITER)
        if cut != -1:
            tail = buffer[emitted:cut].rstrip()
            if tail:
                yield tail
            past_delimiter = True
            continue

        # hold back the last few chars: they might be a half-arrived delimiter
        safe = len(buffer) - (len(DELIMITER) - 1)
        if safe > emitted:
            yield buffer[emitted:safe]
            emitted = safe

    if not past_delimiter:
        tail = buffer[emitted:].rstrip()
        if tail:
            yield tail


async def query_events(
    question: str,
    document_ids: list[UUID] | None = None,
) -> AsyncIterator[dict[str, str]]:
    start = time.perf_counter()
    ttft_s: float | None = None

    pool = await get_pool()
    async with pool.acquire() as conn:
        retrieved = await hybrid.search(conn, question)

    if document_ids is not None:
        retrieved = [c for c in retrieved if c.document_id in document_ids]

    labelled = label_chunks(retrieved)

    raw_parts: list[str] = []
    prose_parts: list[str] = []
    tokens, stream_meta = generate_stream(question, labelled)
    async for prose in _stream_prose(tokens, raw_parts):
        if ttft_s is None:
            ttft_s = time.perf_counter() - start
        prose_parts.append(prose)
        yield {"event": "token", "data": prose}

    result = _finalize("".join(raw_parts), labelled)
    result = GenerationResult(
        answer="".join(prose_parts).strip(),
        citations=result.citations,
        confidence=result.confidence,
    )
    payload = _to_response(result, retrieved, labelled)
    yield {"event": "done", "data": json.dumps(payload.model_dump())}

    total_s = time.perf_counter() - start
    entry = QueryLogEntry(
        id=uuid4(),
        question=question,
        document_ids=document_ids,
        chunk_ids_retrieved=[c.chunk_id for c in retrieved],
        ttft_s=ttft_s,
        total_s=total_s,
        input_tokens=stream_meta.input_tokens,
        output_tokens=stream_meta.output_tokens,
        refused=result.answer.strip() == REFUSAL_MESSAGE,
    )
    try:
        async with pool.acquire() as conn:
            await insert_query_log(conn, entry)
    except Exception:
        logger.exception("failed to write query log")


async def run_query(
    question: str,
    document_ids: list[UUID] | None = None,
) -> QueryResponse:
    async for event in query_events(question, document_ids):
        if event["event"] == "done":
            return QueryResponse.model_validate_json(event["data"])
    raise RuntimeError("stream ended without done event")
