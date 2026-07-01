from __future__ import annotations

from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.report import render_metrics_md
from leaseclear.evals.types import CaseResult, ClaimJudgment, JudgeVerdict
from leaseclear.types import GenerationResult, ValidationResult


def _case() -> CaseResult:
    return CaseResult(
        item_id="golden-001",
        item_type="answerable",
        question="What is the rent?",
        retrieved=[],
        retrieval_hit=True,
        result=GenerationResult(
            answer="$1,875.00 [lease §3]", citations=[], confidence=1.0
        ),
        validation=ValidationResult(passed=True, phantom_ids=[], uncited_claims=False),
        refused=False,
        expected_refusal=False,
        correctly_refused=True,
        judge=JudgeVerdict(
            claims=[
                ClaimJudgment(
                    "Rent is $1,875.00",
                    ["[lease §3]"],
                    supported_by_citation=True,
                    supported_by_context=True,
                )
            ]
        ),
        ttft_s=0.42,
        total_s=0.9,
        input_tokens=100,
        output_tokens=50,
    )


def test_render_metrics_md_contains_table_and_metadata() -> None:
    results = [_case()]
    metrics = aggregate_metrics(results)
    md = render_metrics_md(metrics, results)

    assert md.startswith("# METRICS")
    assert "Retrieval recall@8" in md
    assert "Faithfulness (LLM-as-judge)" in md
    assert "Citation precision" in md
    assert "Refusal accuracy" in md
    assert "Hallucination rate" in md
    assert "gpt-4o-mini" in md
    assert "golden-001" in md
    assert "1 golden items" in md


def test_render_metrics_md_handles_empty_results() -> None:
    metrics = aggregate_metrics([])
    md = render_metrics_md(metrics, [])
    assert "n/a" in md
    assert "0 golden items" in md
