from __future__ import annotations

import asyncpg
import pytest

from leaseclear.retrieval.vector import search
from leaseclear.types import ChunkBase
from tests.data.corpus import CORPUS_LEASE_DOCUMENT_ID
from tests.retrieval.data.vector_search_cases import as_pytest_params


@pytest.mark.real_api
@pytest.mark.parametrize("question,expected_clause_number", as_pytest_params())
async def test_vector_search_returns_relevant_clause(
    seed_db: asyncpg.Connection,
    question: str,
    expected_clause_number: str,
) -> None:
    results: list[ChunkBase] = await search(question, top_k=5)

    assert results
    assert all(result.document_id == CORPUS_LEASE_DOCUMENT_ID for result in results)

    top_numbers = [result.clause_number for result in results[:3]]
    assert expected_clause_number in top_numbers, (
        f"expected {expected_clause_number!r} in top 3 for {question!r}, "
        f"got {top_numbers!r}"
    )
