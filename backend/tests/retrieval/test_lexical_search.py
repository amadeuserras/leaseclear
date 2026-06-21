from __future__ import annotations

import asyncpg

from leaseclear.retrieval.lexical import search


async def test_lexical_search_matches_exact_clause_heading(
    seeded_db: asyncpg.Connection,
) -> None:
    results = await search(seeded_db, "Security Deposit", top_k=5)

    assert results
    assert results[0].clause_label == "5. Security Deposit"


async def test_lexical_search_returns_empty_for_unknown_section_reference(
    seeded_db: asyncpg.Connection,
) -> None:
    results = await search(seeded_db, "Section 8.3", top_k=5)

    assert results == []
