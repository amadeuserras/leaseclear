from __future__ import annotations

import asyncpg
import pytest

from leaseclear.retrieval.vector import search
from leaseclear.types import ChunkBase
from tests.retrieval.data.vector_search_cases import as_pytest_params


@pytest.mark.real_api
@pytest.mark.parametrize("question,expected_clause", as_pytest_params())
async def test_vector_search_returns_relevant_clause(
    seeded_db: asyncpg.Connection,
    question: str,
    expected_clause: str,
) -> None:
    results: list[ChunkBase] = await search(seeded_db, question, top_k=5)

    assert results
    assert all(result.document_id == "lease" for result in results)

    top_labels = [result.clause_label for result in results[:3]]
    assert expected_clause in top_labels, (
        f"expected {expected_clause!r} in top 3 for {question!r}, got {top_labels!r}"
    )
