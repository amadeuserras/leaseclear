from __future__ import annotations

import asyncio
import logging
import random
from uuid import UUID

from leaseclear.api.schemas import SuggestedQuestionsResponse
from leaseclear.db.connection import db_session
from leaseclear.filtering.documents import get_chunks_by_documents, get_documents
from leaseclear.generation.questions import generate_questions

logger = logging.getLogger(__name__)

POOL_SIZE = 15
SAMPLE_SIZE = 4

_pool_cache: dict[frozenset[UUID], list[str]] = {}
_lock = asyncio.Lock()


async def _question_pool(user_id: UUID) -> list[str]:
    async with db_session():
        documents = await get_documents(user_id)
        if not documents:
            return []

        key = frozenset(d.id for d in documents)
        cached = _pool_cache.get(key)
        if cached is not None:
            return cached

        chunks = await get_chunks_by_documents([d.id for d in documents])

    async with _lock:
        cached = _pool_cache.get(key)
        if cached is not None:
            return cached
        try:
            pool = await generate_questions(chunks, documents, POOL_SIZE)
        except Exception:
            logger.exception("failed to generate suggested questions")
            return []
        _pool_cache[key] = pool
        return pool


async def get_suggested_questions(user_id: UUID) -> SuggestedQuestionsResponse:
    pool = await _question_pool(user_id)
    sample = random.sample(pool, min(SAMPLE_SIZE, len(pool)))
    return SuggestedQuestionsResponse(questions=sample)
