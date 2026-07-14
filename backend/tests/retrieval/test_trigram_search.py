from __future__ import annotations

import asyncpg

from leaseclear.retrieval.trigram import search


async def test_trigram_search_ranks_named_tenant_chunk_first(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("What did Priya Nadkarni sign?", top_k=5)

    assert results
    assert "Nadkarni" in results[0].text


async def test_trigram_search_tolerates_misspelled_names(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("pet deposit for Danel Osey", top_k=5)

    assert results
    assert results[0].clause_title == "Pet Deposit and Rent"


async def test_trigram_search_floor_filters_unrelated_questions(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("zzyzx qwxyzzy", top_k=5)

    assert results == []
