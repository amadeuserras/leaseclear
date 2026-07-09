from __future__ import annotations

import asyncio
import logging
import random
from collections import defaultdict
from uuid import UUID

from leaseclear.api.schemas import SuggestedQuestionsResponse
from leaseclear.db.connection import db_session
from leaseclear.generation.questions import generate_questions
from leaseclear.ingestion.documents import get_chunks_by_documents, get_documents
from leaseclear.types import ChunkBase, DocumentMetadata

logger = logging.getLogger(__name__)

POOL_PER_DOCUMENT = 6
SAMPLE_SIZE = 4
# We only ever render SAMPLE_SIZE chips, so we just need a small working set of
# documents with cached questions to sample from, not one per document. A
# 400-lease upload warms ~WORKING_SET_SIZE of them, not 400.
WORKING_SET_SIZE = 10
GENERATION_CONCURRENCY = 5

_question_cache: dict[UUID, list[str]] = {}
_inflight: set[UUID] = set()
_lock = asyncio.Lock()
_semaphore = asyncio.Semaphore(GENERATION_CONCURRENCY)


async def _generate_one(doc: DocumentMetadata, chunks: list[ChunkBase]) -> None:
    async with _semaphore:
        try:
            questions: list[str] | None = await generate_questions(
                chunks, doc, POOL_PER_DOCUMENT
            )
        except Exception:
            logger.exception("failed to generate suggested questions for %s", doc.slug)
            questions = None  # leave uncached so a later request can retry
    async with _lock:
        _inflight.discard(doc.id)
        if questions is not None:
            _question_cache[doc.id] = questions


async def _ensure_cached(
    documents: list[DocumentMetadata], chunks_by_doc: dict[UUID, list[ChunkBase]]
) -> None:
    async with _lock:
        to_generate = [
            d
            for d in documents
            if d.id not in _question_cache and d.id not in _inflight
        ]
        _inflight.update(d.id for d in to_generate)

    if not to_generate:
        return
    await asyncio.gather(
        *(_generate_one(d, chunks_by_doc.get(d.id, [])) for d in to_generate)
    )


def _sample(questions_by_doc: dict[UUID, list[str]], count: int) -> list[str]:
    # Round-robin across documents so a mixed selection surfaces questions about
    # different leases rather than clustering on one.
    buckets = [random.sample(qs, len(qs)) for qs in questions_by_doc.values() if qs]
    random.shuffle(buckets)
    sample: list[str] = []
    while len(sample) < count and any(buckets):
        for bucket in buckets:
            if bucket:
                sample.append(bucket.pop())
                if len(sample) == count:
                    break
    return sample


async def get_suggested_questions(
    user_id: UUID, document_ids: list[UUID] | None = None
) -> SuggestedQuestionsResponse:
    async with db_session():
        documents = await get_documents(user_id)

    if document_ids is not None:
        selected = set(document_ids)
        documents = [d for d in documents if d.id in selected]
    if not documents:
        return SuggestedQuestionsResponse(questions=[])

    cached = [d for d in documents if d.id in _question_cache]
    uncached = [d for d in documents if d.id not in _question_cache]
    need = min(WORKING_SET_SIZE, len(documents)) - len(cached)

    if need > 0 and uncached:
        picks = random.sample(uncached, min(need, len(uncached)))
        async with db_session():
            chunks = await get_chunks_by_documents([d.id for d in picks])
        chunks_by_doc: dict[UUID, list[ChunkBase]] = defaultdict(list)
        for chunk in chunks:
            chunks_by_doc[chunk.document_id].append(chunk)
        await _ensure_cached(picks, chunks_by_doc)

    questions_by_doc = {d.id: _question_cache.get(d.id, []) for d in documents}
    return SuggestedQuestionsResponse(questions=_sample(questions_by_doc, SAMPLE_SIZE))
