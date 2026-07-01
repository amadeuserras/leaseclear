from __future__ import annotations

import pytest

from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.report import render_metrics_md
from leaseclear.evals.types import CaseResult

pytestmark = pytest.mark.eval


async def test_golden_suite_meets_targets(case_results: list[CaseResult]) -> None:
    metrics = aggregate_metrics(case_results)
    print(render_metrics_md(metrics, case_results))

    errors = [r for r in case_results if r.error]
    assert not errors, errors

    for score in (
        metrics.retrieval_recall_at_8,
        metrics.faithfulness,
        metrics.citation_precision,
        metrics.refusal_accuracy,
        metrics.hallucination_rate,
    ):
        # `passed is not False` (not plain truthiness): a metric with no
        # applicable cases yet (None) shouldn't fail the run.
        assert score.passed is not False, score
