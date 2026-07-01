from __future__ import annotations

import datetime as dt

from leaseclear.evals.metrics import AggregateMetrics, MetricScore
from leaseclear.evals.types import CaseResult

JUDGE_NOTE = (
    "The judge is OpenAI `gpt-4o-mini` — a different model family from the "
    "generator (Anthropic Claude). A model is a poor judge of its own answers: "
    "it tends to share the same blind spots that produced the answer in the "
    "first place. Grading with a different family means the judge's failure "
    "modes don't systematically line up with the generator's."
)

BEFORE_AFTER = (
    "**Before/after — hybrid retrieval (CP4).** On the hand-checked MRR "
    "comparison set (`tests/retrieval/data/mrr_comparison_cases.py`), "
    "vector-only search scores MRR ≈ 0.83 and lexical-only ≈ 0.41 "
    '(Postgres FTS is currently weak on currency tokens like "$40" and on '
    "AND-joined filler-word queries). Fusing both with Reciprocal Rank Fusion "
    "ties the best single retriever (hybrid ≈ 0.83) rather than being "
    "dragged down by the weaker one. The win here is robustness, not a raw "
    "MRR jump — lexical isn't yet strong enough to out-rank vector on any "
    "case in that set, so a genuine hybrid *win* is the next retrieval "
    "improvement to chase once lexical search is tuned."
)


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _fmt_s(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}s"


def _row(label: str, score: MetricScore) -> str:
    direction = "≥" if score.higher_is_better else "≤"
    target = f"{direction} {score.target * 100:.0f}%"
    status = "n/a" if score.passed is None else ("PASS" if score.passed else "FAIL")
    return f"| {label} | {_fmt_pct(score.value)} | {target} | {score.n} | {status} |"


def render_metrics_md(metrics: AggregateMetrics, results: list[CaseResult]) -> str:
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# METRICS",
        "",
        f"_Generated {generated} by `scripts/run_evals.py` against "
        f"{metrics.n_cases} golden items ({metrics.n_errors} errored)._",
        "",
        "The golden dataset (`backend/src/leaseclear/evals/golden/golden.jsonl`) "
        "is intentionally small right now while the harness is being proven "
        "out. CP7's target shape is ~70 items (40 answerable, 15 unanswerable, "
        "15 hard). Treat `n` below as a caveat on every number, not a footnote "
        "— a metric on 2-10 cases is a smoke test, not a claim.",
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
        "## Methodology",
        "",
        "- **Retrieval recall@8** — for every golden item with a ground-truth "
        "clause (or page, when no clause number applies), did hybrid search's "
        "top-8 chunks (vector + lexical, RRF-fused) include it? Unanswerable "
        "items have no ground-truth clause and are excluded.",
        "- **Faithfulness / citation precision / hallucination rate** — the "
        "judge splits each non-refusal answer into atomic claims and checks "
        "each one against (a) the full retrieved set (`supported_by_context`, "
        "drives faithfulness and hallucination rate) and (b) specifically the "
        "clause(s) the answer cited for that claim (`supported_by_citation`, "
        "drives citation precision). All three are pooled over every claim in "
        "the run, not averaged per-case.",
        "- **Refusal accuracy** — of the unanswerable golden items, the "
        "fraction where the system actually produced the refusal message.",
        "- **Hallucination rate** — fraction of claims across the full run "
        "that are not supported by anything in the retrieved context "
        "(unlike citation precision, this ignores which clause was cited).",
        "",
        "## Judge",
        "",
        JUDGE_NOTE,
        "",
        "## Before / after",
        "",
        BEFORE_AFTER,
        "",
        "## Per-case results",
        "",
        "| id | type | retrieval hit | refusal correct | faithfulness | "
        "citation precision | ttft (s) |",
        "|---|---|---|---|---|---|---|",
    ]

    for r in results:
        hit = "n/a" if r.retrieval_hit is None else ("yes" if r.retrieval_hit else "no")
        refusal_ok = "yes" if r.correctly_refused else "no"
        faith = _fmt_pct(r.judge.faithfulness) if r.judge else "n/a"
        prec = _fmt_pct(r.judge.citation_precision) if r.judge else "n/a"
        ttft = "n/a" if r.ttft_s is None else f"{r.ttft_s:.2f}"
        error = f" _(error: {r.error})_" if r.error else ""
        lines.append(
            f"| {r.item_id} | {r.item_type} | {hit} | {refusal_ok} | "
            f"{faith} | {prec} | {ttft}{error} |"
        )

    lines.append("")
    return "\n".join(lines)
