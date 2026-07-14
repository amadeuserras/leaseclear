from __future__ import annotations

import dataclasses
import datetime as dt
import json
from typing import Any

from leaseclear.evals.generation.metrics import AggregateMetrics, MetricScore
from leaseclear.evals.generation.types import CaseResult, JudgeVerdict
from leaseclear.generation.generate import _build_user_message


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _fmt_s(value: float | None) -> str:
    return "n/a" if value is None else f"{value:.2f}s"


def _row(label: str, score: MetricScore) -> str:
    direction = "≥" if score.higher_is_better else "≤"
    target = f"{direction} {score.target * 100:.0f}%"
    status = "n/a" if score.passed is None else ("PASS" if score.passed else "FAIL")
    return f"| {label} | {_fmt_pct(score.value)} | {target} | {score.n} | {status} |"


def _section(title: str, body: list[str]) -> list[str]:
    return [f"**{title}**", ""] + body + [""]


def _text_fence(text: str) -> list[str]:
    return ["```", text, "```"]


def _json_fence(data: Any) -> list[str]:
    return [
        "```json",
        json.dumps(data, indent=2, default=str, ensure_ascii=False),
        "```",
    ]


def _judge_data(verdict: JudgeVerdict) -> dict[str, Any]:
    data = dataclasses.asdict(verdict)
    data["faithfulness"] = verdict.faithfulness
    data["citation_precision"] = verdict.citation_precision
    data["hallucination_rate"] = verdict.hallucination_rate
    return data


def _generation_body(result: CaseResult) -> list[str]:
    citation_ids = [c.id for c in result.result.citations]
    body = _text_fence(result.result.answer)
    if citation_ids:
        body += [""] + _json_fence(citation_ids)
    return body


def _render_case(result: CaseResult) -> list[str]:
    user_message = _build_user_message(
        result.question, result.retrieved, result.documents
    )
    lines = [f"### {result.item_id}", ""]
    lines.extend(_section("User message", _text_fence(user_message)))
    lines.extend(_section("Generation result", _generation_body(result)))
    golden_answer = result.expected_answer or "(Refusal)"
    lines.extend(_section("Golden Answer", _text_fence(golden_answer)))
    if result.answer_match is not None:
        lines.extend(
            _section("Answer match", _json_fence({"matches": result.answer_match}))
        )
    lines.extend(
        _section("Validation", _json_fence(dataclasses.asdict(result.validation)))
    )
    lines.extend(
        _section(
            "Refusal",
            _json_fence(
                {
                    "refused": result.refused,
                    "expected_refusal": result.expected_refusal,
                }
            ),
        )
    )
    if result.judge is not None:
        lines.extend(_section("Judge", _json_fence(_judge_data(result.judge))))
    return lines


def render_metrics_md(metrics: AggregateMetrics, results: list[CaseResult]) -> str:
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# METRICS",
        "",
        f"_Generated {generated} by `scripts/run_eval.py --mode generation` against "
        f"{metrics.n_cases} golden items ({metrics.n_errors} errored)._",
        "",
        "| Metric | Score | Target | n | Status |",
        "|---|---|---|---|---|",
        _row(
            "Retrieval recall@8 – golden chunk was retrieved in the top 8 chunks",
            metrics.retrieval_recall_at_8,
        ),
        _row(
            "Faithfulness (LLM) – claims supported by retrieved chunks",
            metrics.faithfulness,
        ),
        _row(
            "Citation precision (LLM) – claims supported by cited chunks",
            metrics.citation_precision,
        ),
        _row("Refusal accuracy", metrics.refusal_accuracy),
        _row(
            "Answer match (LLM) – generated answer matches golden answer",
            metrics.answer_match,
        ),
        _row(
            "Hallucination rate (LLM) – claims not supported by retrieved chunks",
            metrics.hallucination_rate,
        ),
        "",
        f"p95 time-to-first-token – time until the first streamed token appears: "
        f"{_fmt_s(metrics.p95_ttft_s)} (target < 1.5s)",
        "",
        f"p95 total query latency – time until the full answer is generated: "
        f"{_fmt_s(metrics.p95_total_s)}",
        "",
        "## Per-case results",
        "",
    ]

    for r in results:
        lines.extend(_render_case(r))

    return "\n".join(lines)
