from __future__ import annotations

from uuid import uuid4

import asyncpg

from leaseclear.retrieval.vector import search
from leaseclear.types import ChunkBase


async def test_vector_search_returns_chunk_base_objects(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("What is the monthly rent?", top_k=5, similarity_floor=None)

    assert results
    assert all(isinstance(r, ChunkBase) for r in results)


async def test_vector_search_respects_top_k(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("rent", top_k=2)

    assert len(results) <= 2


async def test_vector_search_filters_by_document_id(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("rent", top_k=10, document_ids=[uuid4()])

    assert results == []
