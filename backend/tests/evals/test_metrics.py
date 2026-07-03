from __future__ import annotations

from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.types import CaseResult, ClaimJudgment, JudgeVerdict
from leaseclear.types import GenerationResult, ValidationResult


def _case(
    item_type: str,
    retrieval_hit: bool | None,
    claims: list[ClaimJudgment] | None,
) -> CaseResult:
    return CaseResult(
        item_id="1",
        item_type=item_type,
        question="q",
        retrieved=[],
        documents=[],
        retrieval_hit=retrieval_hit,
        result=GenerationResult(answer="a", citations=[]),
        validation=ValidationResult(passed=True, phantom_ids=[], uncited_claims=False),
        refused=False,
        expected_refusal=False,
        judge=JudgeVerdict(claims=claims) if claims is not None else None,
        ttft_s=0.5,
        total_s=0.6,
        input_tokens=10,
        output_tokens=20,
    )


def test_aggregate_metrics_computes_expected_scores() -> None:
    claim = ClaimJudgment(
        "c", ["[a]"], supported_by_citation=True, supported_by_context=True
    )
    results = [
        _case("answerable", True, [claim]),
        _case("unanswerable", None, None),
    ]

    metrics = aggregate_metrics(results)

    assert metrics.retrieval_recall_at_8.value == 1.0
    assert metrics.faithfulness.value == 1.0
    assert metrics.refusal_accuracy.value == 1.0
