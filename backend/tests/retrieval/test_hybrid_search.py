from __future__ import annotations

import asyncpg
import pytest

from leaseclear.retrieval import hybrid
from leaseclear.schema import RetrievedChunk


@pytest.mark.real_api
async def test_hybrid_search_ranks_exact_clause_match_first(
    seeded_db: asyncpg.Connection,
) -> None:
    question = "Show me the security deposit section"

    hybrid_results: list[RetrievedChunk] = await hybrid.search(seeded_db, question)

    assert hybrid_results
    assert len(hybrid_results) <= 8
    assert hybrid_results[0].clause_label == "5. Security Deposit"
