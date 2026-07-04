from __future__ import annotations

import statistics
from dataclasses import dataclass

from leaseclear.evals.types import CaseResult, ClaimJudgment

TARGETS = {
    "retrieval_recall_at_8": 0.90,
    "faithfulness": 0.90,
    "citation_precision": 0.90,
    "refusal_accuracy": 0.93,
    "hallucination_rate": 0.05,
}


@dataclass(frozen=True)
class MetricScore:
    name: str
    value: float | None
    target: float
    higher_is_better: bool
    n: int

    @property
    def passed(self) -> bool | None:
        if self.value is None:
            return None
        if self.higher_is_better:
            return self.value >= self.target
        return self.value <= self.target


@dataclass(frozen=True)
class AggregateMetrics:
    retrieval_recall_at_8: MetricScore
    faithfulness: MetricScore
    citation_precision: MetricScore
    refusal_accuracy: MetricScore
    hallucination_rate: MetricScore
    p95_ttft_s: float | None
    p95_total_s: float | None
    n_cases: int
    n_errors: int


def _percentile(values: list[float], p: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return values[0]
    cut_points = statistics.quantiles(values, n=100, method="inclusive")
    return cut_points[int(p) - 1]


def _rate(flags: list[bool]) -> float | None:
    if not flags:
        return None
    return sum(flags) / len(flags)


def aggregate_metrics(results: list[CaseResult]) -> AggregateMetrics:
    recall_flags = [r.retrieval_hit for r in results if r.retrieval_hit is not None]
    recall = MetricScore(
        "retrieval_recall_at_8",
        _rate(recall_flags),
        TARGETS["retrieval_recall_at_8"],
        higher_is_better=True,
        n=len(recall_flags),
    )

    claims: list[ClaimJudgment] = [
        c for r in results if r.judge is not None for c in r.judge.claims
    ]
    faithfulness = MetricScore(
        "faithfulness",
        _rate([c.supported_by_context for c in claims]),
        TARGETS["faithfulness"],
        higher_is_better=True,
        n=len(claims),
    )
    citation_precision = MetricScore(
        "citation_precision",
        _rate([c.supported_by_citation for c in claims]),
        TARGETS["citation_precision"],
        higher_is_better=True,
        n=len(claims),
    )
    hallucination_rate = MetricScore(
        "hallucination_rate",
        _rate([not c.supported_by_context for c in claims]),
        TARGETS["hallucination_rate"],
        higher_is_better=False,
        n=len(claims),
    )

    unanswerable = [r for r in results if r.item_type == "unanswerable"]
    refusal_accuracy = MetricScore(
        "refusal_accuracy",
        _rate([r.refused == r.expected_refusal for r in unanswerable]),
        TARGETS["refusal_accuracy"],
        higher_is_better=True,
        n=len(unanswerable),
    )

    ttfts = [r.ttft_s for r in results if r.ttft_s is not None]
    totals = [r.total_s for r in results if r.error is None]

    return AggregateMetrics(
        retrieval_recall_at_8=recall,
        faithfulness=faithfulness,
        citation_precision=citation_precision,
        refusal_accuracy=refusal_accuracy,
        hallucination_rate=hallucination_rate,
        p95_ttft_s=_percentile(ttfts, 95),
        p95_total_s=_percentile(totals, 95),
        n_cases=len(results),
        n_errors=sum(1 for r in results if r.error is not None),
    )
