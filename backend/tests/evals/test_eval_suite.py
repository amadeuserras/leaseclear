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
    assert not errors, f"{len(errors)} golden item(s) errored: {errors}"

    # `passed is not False` rather than a plain truthiness check: a metric
    # with no applicable cases (value/passed is None) shouldn't fail a run on
    # a golden set too small to exercise it yet. Only an explicit below-target
    # score should fail the build.
    assert metrics.retrieval_recall_at_8.passed is not False, (
        metrics.retrieval_recall_at_8
    )
    assert metrics.faithfulness.passed is not False, metrics.faithfulness
    assert metrics.citation_precision.passed is not False, metrics.citation_precision
    assert metrics.refusal_accuracy.passed is not False, metrics.refusal_accuracy
    assert metrics.hallucination_rate.passed is not False, metrics.hallucination_rate
