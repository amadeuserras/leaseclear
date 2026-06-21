from __future__ import annotations

import asyncpg
import pytest

from leaseclear.retrieval.search import search
from tests.retrieval.data.search_cases_lease import SEARCH_CASES_LEASE


@pytest.mark.real_api
@pytest.mark.parametrize("question,expected_clause", SEARCH_CASES_LEASE)
async def test_search_returns_relevant_clause(
    seeded_db: asyncpg.Connection,
    question: str,
    expected_clause: str,
) -> None:
    results = await search(seeded_db, question, top_k=5)

    assert results
    assert all(result.document_id == "lease" for result in results)

    similarities = [result.similarity for result in results]
    assert similarities == sorted(similarities, reverse=True)

    top_labels = [result.clause_label for result in results[:3]]
    assert expected_clause in top_labels, (
        f"expected {expected_clause!r} in top 3 for {question!r}, got {top_labels!r}"
    )
