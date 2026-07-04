from __future__ import annotations

import asyncpg

from leaseclear.retrieval.lexical import search


async def test_lexical_search_matches_exact_clause_heading(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("Security Deposit", top_k=5)

    assert results
    assert results[0].clause_number == "5"


async def test_lexical_search_survives_terms_absent_from_corpus(
    seed_db: asyncpg.Connection,
) -> None:
    # "spaceship" appears nowhere; AND semantics would return zero rows.
    results = await search("security deposit for the spaceship", top_k=5)

    assert results
    assert results[0].clause_number == "5"


async def test_lexical_search_splits_slash_joined_names(
    seed_db: asyncpg.Connection,
) -> None:
    # plainto_tsquery kept "nadkarni/osei" as one lexeme that no chunk
    # contains; the words must be matched individually.
    results = await search("May the Nadkarni/Osei tenants keep a dog?", top_k=10)

    assert any("Nadkarni" in chunk.text for chunk in results)


async def test_lexical_search_returns_empty_for_no_matching_words(
    seed_db: asyncpg.Connection,
) -> None:
    results = await search("zzyzx qwxyzzy", top_k=5)

    assert results == []
