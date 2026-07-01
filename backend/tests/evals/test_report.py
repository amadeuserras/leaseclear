from __future__ import annotations

from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.report import render_metrics_md
from leaseclear.evals.types import CaseResult
from leaseclear.types import GenerationResult, ValidationResult


def test_render_metrics_md_includes_table_and_case_data() -> None:
    result = CaseResult(
        item_id="golden-001",
        item_type="answerable",
        question="q",
        retrieved=[],
        retrieval_hit=True,
        result=GenerationResult(answer="a", citations=[], confidence=1.0),
        validation=ValidationResult(passed=True, phantom_ids=[], uncited_claims=False),
        refused=False,
        expected_refusal=False,
        correctly_refused=True,
        judge=None,
        ttft_s=0.5,
        total_s=0.6,
        input_tokens=10,
        output_tokens=20,
    )
    metrics = aggregate_metrics([result])

    md = render_metrics_md(metrics, [result])

    assert "Retrieval recall@8" in md
    assert "golden-001" in md
