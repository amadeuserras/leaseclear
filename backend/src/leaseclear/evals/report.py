from __future__ import annotations

import dataclasses
import datetime as dt
import json

from leaseclear.evals.metrics import AggregateMetrics, MetricScore
from leaseclear.evals.types import CaseResult


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _fmt_s(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}s"


def _row(label: str, score: MetricScore) -> str:
    direction = "≥" if score.higher_is_better else "≤"
    target = f"{direction} {score.target * 100:.0f}%"
    status = "n/a" if score.passed is None else ("PASS" if score.passed else "FAIL")
    return f"| {label} | {_fmt_pct(score.value)} | {target} | {score.n} | {status} |"


def _case_dump(result: CaseResult) -> str:
    data = dataclasses.asdict(result)
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


def render_metrics_md(metrics: AggregateMetrics, results: list[CaseResult]) -> str:
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# METRICS",
        "",
        f"_Generated {generated} by `scripts/run_evals.py` against "
        f"{metrics.n_cases} golden items ({metrics.n_errors} errored)._",
        "",
        "| Metric | Score | Target | n | Status |",
        "|---|---|---|---|---|",
        _row("Retrieval recall@8", metrics.retrieval_recall_at_8),
        _row("Faithfulness (LLM-as-judge)", metrics.faithfulness),
        _row("Citation precision", metrics.citation_precision),
        _row("Refusal accuracy", metrics.refusal_accuracy),
        _row("Hallucination rate", metrics.hallucination_rate),
        "",
        f"p95 time-to-first-token: {_fmt_s(metrics.p95_ttft_s)} (target < 1.5s)",
        "",
        f"p95 total query latency: {_fmt_s(metrics.p95_total_s)}",
        "",
        "## Per-case results",
        "",
    ]

    for r in results:
        lines.append(f"### {r.item_id}")
        lines.append("")
        lines.append("```json")
        lines.append(_case_dump(r))
        lines.append("```")
        lines.append("")

    return "\n".join(lines)
