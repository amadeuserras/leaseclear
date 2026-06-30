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
from leaseclear.generation.parse import parse_response, resolve_citations
from leaseclear.generation.prompts import DELIMITER, REFUSAL_MESSAGE
from leaseclear.generation.validate import validate
from leaseclear.retrieval import hybrid
from leaseclear.types import ChunkBase, GenerationResult, QueryLogEntry
from leaseclear.types import Citation as GenCitation

logger = logging.getLogger(__name__)


def _to_response(result: GenerationResult, retrieved: list[ChunkBase]) -> QueryResponse:
    cited = resolve_citations([c.id for c in result.citations], retrieved)
    return QueryResponse(
        answer=result.answer,
        citations=[
            Citation(
                chunk_id=chunk.id,
                clause_label=chunk.clause_label or "",
                page_number=chunk.page_number,
                passage=chunk.text,
            )
            for chunk in cited
        ],
        confidence=result.confidence,
    )


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

    raw_parts: list[str] = []
    prose_parts: list[str] = []
    tokens, stream_meta = generate_stream(question, retrieved)
    async for prose in _stream_prose(tokens, raw_parts):
        if ttft_s is None:
            ttft_s = time.perf_counter() - start
        prose_parts.append(prose)
        yield {"event": "token", "data": prose}

    prose, citation_ids, confidence = parse_response("".join(raw_parts))
    result = GenerationResult(
        answer="".join(prose_parts).strip(),
        citations=[GenCitation(id=cid) for cid in citation_ids],
        confidence=confidence,
    )
    validate(result, retrieved, REFUSAL_MESSAGE)
    payload = _to_response(result, retrieved)
    yield {"event": "done", "data": json.dumps(payload.model_dump())}

    total_s = time.perf_counter() - start
    entry = QueryLogEntry(
        id=uuid4(),
        question=question,
        document_ids=document_ids,
        chunk_ids_retrieved=[c.id for c in retrieved],
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
