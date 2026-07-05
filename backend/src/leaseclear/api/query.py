from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

from leaseclear.api.schemas import Citation, QueryResponse
from leaseclear.db.connection import db_session
from leaseclear.db.logs import insert_query_log
from leaseclear.filtering.documents import get_documents
from leaseclear.filtering.filter import filter_documents
from leaseclear.generation.generate import generate_stream
from leaseclear.generation.parse import parse_response, resolve_citations
from leaseclear.generation.prompts import DELIMITER, REFUSAL_MESSAGE
from leaseclear.generation.validate import is_refusal, validate
from leaseclear.retrieval import hybrid
from leaseclear.types import ChunkBase, GenerationResult, ParsedResponse, QueryLogEntry
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
    user_id: UUID,
    document_ids: list[UUID] | None = None,
) -> AsyncIterator[dict[str, str]]:
    start = time.perf_counter()
    ttft_s: float | None = None

    async with db_session():
        user_docs = await get_documents(user_id)

    if document_ids:
        document_ids_set = set(document_ids)
        authorized_docs = [d for d in user_docs if d.id in document_ids_set]
    else:
        authorized_docs = user_docs

    filtered_ids = await filter_documents(question, authorized_docs)
    filtered_ids_set = set(filtered_ids)
    filtered_docs = [d for d in authorized_docs if d.id in filtered_ids_set]

    async with db_session():
        retrieved_chunks = await hybrid.search(question, document_ids=filtered_ids)

    raw_parts: list[str] = []
    prose_parts: list[str] = []
    tokens, stream_meta = generate_stream(question, retrieved_chunks, filtered_docs)
    async for prose in _stream_prose(tokens, raw_parts):
        if ttft_s is None:
            ttft_s = time.perf_counter() - start
        prose_parts.append(prose)
        yield {"event": "token", "data": prose}

    parsed: ParsedResponse = parse_response("".join(raw_parts))
    result = GenerationResult(
        answer="".join(prose_parts).strip(),
        citations=[GenCitation(id=cid) for cid in parsed.citation_ids],
    )
    validate(result, retrieved_chunks, REFUSAL_MESSAGE)
    payload = _to_response(result, retrieved_chunks)
    yield {"event": "done", "data": payload.model_dump_json()}

    total_s = time.perf_counter() - start
    entry = QueryLogEntry(
        id=uuid4(),
        user_id=user_id,
        question=question,
        document_ids=document_ids,
        chunk_ids_retrieved=[c.id for c in retrieved_chunks],
        ttft_s=ttft_s,
        total_s=total_s,
        input_tokens=stream_meta.input_tokens,
        output_tokens=stream_meta.output_tokens,
        refused=is_refusal(result, REFUSAL_MESSAGE),
    )
    try:
        async with db_session():
            await insert_query_log(entry)
    except Exception:
        logger.exception("failed to write query log")


async def run_query(
    question: str,
    user_id: UUID,
    document_ids: list[UUID] | None = None,
) -> QueryResponse:
    async for event in query_events(question, user_id, document_ids):
        if event["event"] == "done":
            return QueryResponse.model_validate_json(event["data"])
    raise RuntimeError("stream ended without done event")
