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

# Cached per document id: uploading or deleting one lease only regenerates that
# lease's questions instead of the whole corpus.
_question_cache: dict[UUID, list[str]] = {}
_lock = asyncio.Lock()


async def _ensure_cached(
    documents: list[DocumentMetadata], chunks_by_doc: dict[UUID, list[ChunkBase]]
) -> None:
    async with _lock:
        missing = [d for d in documents if d.id not in _question_cache]
        if not missing:
            return
        results = await asyncio.gather(
            *(
                generate_questions(chunks_by_doc.get(d.id, []), d, POOL_PER_DOCUMENT)
                for d in missing
            ),
            return_exceptions=True,
        )
        for doc, result in zip(missing, results, strict=True):
            if isinstance(result, BaseException):
                logger.exception(
                    "failed to generate suggested questions for %s",
                    doc.slug,
                    exc_info=result,
                )
                continue
            _question_cache[doc.id] = result


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

    uncached = [d for d in documents if d.id not in _question_cache]
    if uncached:
        async with db_session():
            chunks = await get_chunks_by_documents([d.id for d in uncached])
        chunks_by_doc: dict[UUID, list[ChunkBase]] = defaultdict(list)
        for chunk in chunks:
            chunks_by_doc[chunk.document_id].append(chunk)
        await _ensure_cached(uncached, chunks_by_doc)

    questions_by_doc = {d.id: _question_cache.get(d.id, []) for d in documents}
    return SuggestedQuestionsResponse(questions=_sample(questions_by_doc, SAMPLE_SIZE))
