from __future__ import annotations

from datetime import datetime
from pathlib import Path

from leaseclear.evals.types import AggregateMetrics, EvalResult
from leaseclear.generation.generate import build_user_message
from leaseclear.generation.prompts import REFUSAL_MESSAGE

RESULTS_DIR = Path(__file__).resolve().parent / "results"


def result_path(*, at: datetime | None = None) -> Path:
    stamp = (at or datetime.now()).strftime("%Y-%m-%d_%H%M%S")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    return RESULTS_DIR / f"evals-{stamp}.md"


def _fmt(value: float | None) -> str:
    return "—" if value is None else f"{value:.2%}"


def _format_metrics(metrics: AggregateMetrics) -> str:
    return "\n".join(
        [
            "| Metric | Score |",
            "| --- | ---: |",
            f"| Cases | {metrics.count} |",
            f"| Retrieval recall | {_fmt(metrics.retrieval_recall)} |",
            f"| Refusal accuracy | {_fmt(metrics.refusal_accuracy)} |",
            f"| Answer match | {_fmt(metrics.answer_match)} |",
            f"| Faithfulness | {_fmt(metrics.faithfulness)} |",
            f"| Citation precision | {_fmt(metrics.citation_precision)} |",
        ]
    )


def _format_case(index: int, result: EvalResult) -> str:
    item = result.item
    expected = (
        f'Refuse with: "{REFUSAL_MESSAGE}"'
        if item.expected_refusal
        else (item.expected_answer or "—")
    )
    prompt = build_user_message(item.question, result.retrieved_chunks)
    return "\n".join(
        [
            f"### {index}. {item.id} ({item.type})",
            "",
            f"**Golden document:** `{item.document_slug}`",
            "",
            "#### Prompt sent to Claude",
            "",
            "```",
            prompt,
            "```",
            "",
            "#### Answer",
            "",
            result.answer,
            "",
            "#### Expected",
            "",
            expected,
            "",
            "#### Scores",
            "",
            f"- Retrieval recall: {result.retrieval_recall:.0%}",
            f"- Refusal accuracy: {result.refusal_accuracy:.0%}",
            f"- Answer match: {result.answer_match:.0%}",
            f"- Faithfulness: {_fmt(result.faithfulness)}",
            f"- Citation precision: {_fmt(result.citation_precision)}",
            f"- Validation: {'pass' if result.validation_passed else 'fail'}",
            "",
        ]
    )


def format_report(
    metrics: AggregateMetrics,
    results: list[EvalResult],
    *,
    include_cases: bool = True,
) -> str:
    sections = [
        "# LeaseClear Eval",
        "",
        "## Metrics",
        "",
        _format_metrics(metrics),
        "",
    ]
    if include_cases:
        sections.append("## Cases\n")
        for i, result in enumerate(results, start=1):
            sections.append(_format_case(i, result))
    return "\n".join(sections)


def write_report(
    metrics: AggregateMetrics,
    results: list[EvalResult],
    path: Path,
    *,
    include_cases: bool = True,
) -> None:
    path.write_text(format_report(metrics, results, include_cases=include_cases))
