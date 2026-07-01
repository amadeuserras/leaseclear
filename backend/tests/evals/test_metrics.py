from __future__ import annotations

import pytest

from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.types import CaseResult, ClaimJudgment, JudgeVerdict
from leaseclear.types import GenerationResult, ValidationResult


def _case(
    item_id: str,
    item_type: str,
    retrieval_hit: bool | None,
    correctly_refused: bool,
    claims: list[ClaimJudgment] | None,
    ttft_s: float | None = 0.5,
    error: str | None = None,
) -> CaseResult:
    return CaseResult(
        item_id=item_id,
        item_type=item_type,
        question="q",
        retrieved=[],
        retrieval_hit=retrieval_hit,
        result=GenerationResult(answer="a", citations=[], confidence=1.0),
        validation=ValidationResult(passed=True, phantom_ids=[], uncited_claims=False),
        refused=False,
        expected_refusal=False,
        correctly_refused=correctly_refused,
        judge=JudgeVerdict(claims=claims) if claims is not None else None,
        ttft_s=ttft_s,
        total_s=(ttft_s or 0) + 0.1,
        input_tokens=10,
        output_tokens=20,
        error=error,
    )


def test_recall_averages_only_over_items_with_a_target() -> None:
    results = [
        _case("1", "answerable", True, True, []),
        _case("2", "answerable", False, True, []),
        _case("3", "unanswerable", None, True, None),
    ]
    metrics = aggregate_metrics(results)
    assert metrics.retrieval_recall_at_8.value == 0.5
    assert metrics.retrieval_recall_at_8.n == 2


def test_refusal_accuracy_only_over_unanswerable_items() -> None:
    results = [
        _case("1", "unanswerable", None, True, None),
        _case("2", "unanswerable", None, False, None),
        _case("3", "answerable", True, True, []),
    ]
    metrics = aggregate_metrics(results)
    assert metrics.refusal_accuracy.value == 0.5
    assert metrics.refusal_accuracy.n == 2


def test_faithfulness_precision_and_hallucination_pool_all_claims() -> None:
    claims = [
        ClaimJudgment(
            "c1", ["[a]"], supported_by_citation=True, supported_by_context=True
        ),
        ClaimJudgment(
            "c2", ["[b]"], supported_by_citation=False, supported_by_context=True
        ),
        ClaimJudgment(
            "c3", [], supported_by_citation=False, supported_by_context=False
        ),
    ]
    results = [_case("1", "answerable", True, True, claims)]
    metrics = aggregate_metrics(results)

    assert metrics.faithfulness.value == pytest.approx(2 / 3)
    assert metrics.citation_precision.value == pytest.approx(1 / 3)
    assert metrics.hallucination_rate.value == pytest.approx(1 / 3)
    assert metrics.faithfulness.n == 3


def test_metric_score_pass_fail_respects_direction() -> None:
    claims = [
        ClaimJudgment("c", ["a"], supported_by_citation=True, supported_by_context=True)
    ]
    results = [_case("1", "answerable", True, True, claims)]
    metrics = aggregate_metrics(results)

    assert metrics.faithfulness.passed is True  # 1.0 >= 0.90
    assert metrics.hallucination_rate.passed is True  # 0.0 <= 0.05


def test_metric_score_is_none_when_no_applicable_cases() -> None:
    metrics = aggregate_metrics([])
    assert metrics.retrieval_recall_at_8.value is None
    assert metrics.retrieval_recall_at_8.passed is None
    assert metrics.p95_ttft_s is None


def test_p95_ttft_interpolates_towards_the_slowest_case() -> None:
    results = [
        _case("1", "answerable", True, True, [], ttft_s=0.5),
        _case("2", "answerable", True, True, [], ttft_s=1.2),
    ]
    metrics = aggregate_metrics(results)
    assert metrics.p95_ttft_s is not None
    assert 0.5 < metrics.p95_ttft_s <= 1.2


def test_p95_ttft_with_single_sample_returns_that_sample() -> None:
    results = [_case("1", "answerable", True, True, [], ttft_s=0.75)]
    metrics = aggregate_metrics(results)
    assert metrics.p95_ttft_s == pytest.approx(0.75)


def test_errored_cases_are_counted_and_excluded_from_latency() -> None:
    results = [
        _case("1", "answerable", True, True, [], ttft_s=0.5),
        _case("2", "answerable", None, False, None, ttft_s=None, error="boom"),
    ]
    metrics = aggregate_metrics(results)
    assert metrics.n_cases == 2
    assert metrics.n_errors == 1
