from __future__ import annotations

import asyncpg
import pytest

from leaseclear.retrieval import hybrid, lexical, vector
from leaseclear.utils.pretty_print import pretty_print
from tests.retrieval.data.mrr_comparison_cases import CASES
from tests.retrieval.metrics import mean_reciprocal_rank, reciprocal_rank

# Snapshot on demo corpus:
#   vector ≈ 0.83   lexical ≈ 0.41   hybrid ≈ 0.83
#
# Read: hybrid TIES vector. Lexical is currently
# weak on currency tokens ($40.00 vs "$40") and AND-joined filler words
# ("show me..."), which caps its score. The takeaway is robustness: hybrid tracks the BEST
# available retriever even while one component (lexical) is degraded — fusion doesn't drag it down.
#
# A genuine hybrid WIN requires a query where vector ranks the clause low
# but lexical ranks it high. That depends on fixing lexical first.


@pytest.mark.real_api
async def test_search_mrr_comparison(seed_db: asyncpg.Connection) -> None:
    hybrid_rrs: list[float] = []
    lexical_rrs: list[float] = []
    vector_rrs: list[float] = []

    for case in CASES:
        hybrid_results = await hybrid.search(seed_db, case.query)
        lexical_results = await lexical.search(seed_db, case.query)
        vector_results = await vector.search(seed_db, case.query)

        hybrid_rrs.append(reciprocal_rank(hybrid_results, case.expected_clause))
        lexical_rrs.append(reciprocal_rank(lexical_results, case.expected_clause))
        vector_rrs.append(reciprocal_rank(vector_results, case.expected_clause))

    scores = {
        "hybrid": mean_reciprocal_rank(hybrid_rrs),
        "lexical": mean_reciprocal_rank(lexical_rrs),
        "vector": mean_reciprocal_rank(vector_rrs),
    }

    for name, mrr in scores.items():
        pretty_print(f"{name}: MRR={mrr:.4f}")
    winner = max(scores, key=lambda k: scores[k])
    pretty_print(f"winner: {winner}")
