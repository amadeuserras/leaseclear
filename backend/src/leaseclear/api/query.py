from __future__ import annotations

import logging
import time
from collections.abc import AsyncIterator
from uuid import UUID, uuid4

from leaseclear.api.schemas import QueryResponse
from leaseclear.db.connection import db_session
from leaseclear.db.logs import insert_query_log
from leaseclear.filtering.filter import filter_documents
from leaseclear.generation.generate import generate_stream
from leaseclear.generation.parse import generation_result_from_answer
from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.generation.validate import is_refusal
from leaseclear.ingestion.documents import get_documents
from leaseclear.retrieval import hybrid
from leaseclear.types import QueryLogEntry

logger = logging.getLogger(__name__)


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

    answer_parts: list[str] = []
    tokens, stream_meta = generate_stream(question, retrieved_chunks, filtered_docs)
    async for token in tokens:
        if ttft_s is None:
            ttft_s = time.perf_counter() - start
        answer_parts.append(token)
        yield {"event": "token", "data": token}

    result = generation_result_from_answer("".join(answer_parts))
    payload = QueryResponse(answer=result.answer)
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
