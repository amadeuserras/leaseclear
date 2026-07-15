from __future__ import annotations

import datetime as dt
from pathlib import Path


def _rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def _generation_excerpt(text: str) -> str:
    marker = "## Per-case results"
    if marker in text:
        text = text.split(marker, 1)[0]
    return text.strip()


def _strip_h1(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        if lines and lines[0] == "":
            lines = lines[1:]
    return "\n".join(lines).strip()


def _demote_headings(text: str) -> str:
    """Demote ATX headings one level so excerpts nest under summary sections."""
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            lines.append("#" + line)
        else:
            lines.append(line)
    return "\n".join(lines)


def render_evals_md(
    *,
    generation_report: Path | None,
    retrieval_report: Path | None,
    repo_root: Path,
) -> str:
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Eval summary",
        "",
        f"_Generated {generated} by `scripts/run_eval.py`._",
        "",
    ]

    links: list[str] = []
    if generation_report is not None:
        links.append(f"[generation report]({_rel(generation_report, repo_root)})")
    if retrieval_report is not None:
        links.append(f"[retrieval report]({_rel(retrieval_report, repo_root)})")
    if links:
        lines.append("Full reports: " + " · ".join(links))
        lines.append("")

    lines.append("## Generation")
    lines.append("")
    if generation_report is None:
        lines.append("_No generation report available yet._")
        lines.append("")
    else:
        excerpt = _demote_headings(
            _strip_h1(_generation_excerpt(generation_report.read_text()))
        )
        lines.append(excerpt)
        lines.append("")

    lines.append("## Retrieval")
    lines.append("")
    if retrieval_report is None:
        lines.append("_No retrieval report available yet._")
        lines.append("")
    else:
        excerpt = _demote_headings(_strip_h1(retrieval_report.read_text().strip()))
        lines.append(excerpt)
        lines.append("")

    return "\n".join(lines)
