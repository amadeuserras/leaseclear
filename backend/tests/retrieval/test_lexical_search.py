from __future__ import annotations

import asyncpg

from leaseclear.retrieval.lexical import search


async def test_lexical_search_matches_exact_clause_heading(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("Security Deposit", top_k=5)

    assert results
    assert results[0].clause_number == "5"


async def test_lexical_search_returns_empty_for_unknown_section_reference(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("Section 8.3", top_k=5)

    assert results == []
