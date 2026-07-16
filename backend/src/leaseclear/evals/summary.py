from __future__ import annotations

import re
from pathlib import Path

from leaseclear.evals.generation.metrics import AggregateMetrics, MetricScore
from leaseclear.evals.retrieval.pipeline import RetrievalEvalResult

GENERATION_DISPLAY = (
    ("Retrieval recall@8", "retrieval_recall_at_8"),
    ("Faithfulness (LLM)", "faithfulness"),
    ("Citation precision (LLM)", "citation_precision"),
    ("Refusal accuracy", "refusal_accuracy"),
    ("Answer match (LLM)", "answer_match"),
    ("Hallucination rate (LLM)", "hallucination_rate"),
)


def _rel(path: Path, repo_root: Path) -> str:
    return "./" + path.resolve().relative_to(repo_root.resolve()).as_posix()


def _fmt_pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _fmt_target(score: MetricScore) -> str:
    direction = "≥" if score.higher_is_better else "≤"
    return f"{direction} {score.target * 100:.0f}%"


def _fmt_status(score: MetricScore) -> str:
    if score.passed is None:
        return "n/a"
    return "PASS" if score.passed else "FAIL"


def _full_report_line(report: Path | None, repo_root: Path) -> str:
    if report is None:
        return "Full report: _none yet._"
    return f"Full report: [{report.name}]({_rel(report, repo_root)})"


def render_generation_readme(
    metrics: AggregateMetrics, *, report: Path | None, repo_root: Path
) -> str:
    lines = [
        "### Generation Summary",
        "",
        "| Metric | Score | Target | n | Status |",
        "|---|---|---|---|---|",
    ]
    for label, attr in GENERATION_DISPLAY:
        score: MetricScore = getattr(metrics, attr)
        lines.append(
            f"| {label} | {_fmt_pct(score.value)} | {_fmt_target(score)} | "
            f"{score.n} | {_fmt_status(score)} |"
        )
    lines.extend(["", _full_report_line(report, repo_root), ""])
    return "\n".join(lines)


def render_retrieval_readme(
    result: RetrievalEvalResult, *, report: Path | None, repo_root: Path
) -> str:
    mrr = result.mrr_winner
    recall = result.recall_winner
    lines = [
        "### Retrieval Summary",
        "",
        "| Metric | Winner Strategy | Score |",
        "|---|---|---|",
        f"| MRR | {mrr.name} | {mrr.mrr:.2f} |",
        f"| Recall@{result.k} | {recall.name} | {recall.recall_at_k:.2f} |",
        "",
        _full_report_line(report, repo_root),
        "",
    ]
    return "\n".join(lines)


def _replace_marked_section(text: str, name: str, body: str) -> str:
    start = f"<!-- {name}:start -->"
    end = f"<!-- {name}:end -->"
    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        flags=re.DOTALL,
    )
    replacement = f"{start}\n{body.rstrip()}\n{end}"
    updated, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise ValueError(f"README.md missing markers for section {name!r}")
    return updated


def update_readme_evals(
    readme_path: Path,
    *,
    repo_root: Path,
    generation_report: Path | None,
    retrieval_report: Path | None,
    generation_metrics: AggregateMetrics | None = None,
    retrieval_result: RetrievalEvalResult | None = None,
) -> None:
    text = readme_path.read_text()
    if generation_metrics is not None:
        text = _replace_marked_section(
            text,
            "eval-generation",
            render_generation_readme(
                generation_metrics, report=generation_report, repo_root=repo_root
            ),
        )
    if retrieval_result is not None:
        text = _replace_marked_section(
            text,
            "eval-retrieval",
            render_retrieval_readme(
                retrieval_result, report=retrieval_report, repo_root=repo_root
            ),
        )
    readme_path.write_text(text)
