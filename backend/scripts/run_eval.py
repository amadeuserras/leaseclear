"""Eval runner.

Usage:
    uv run scripts/run_eval.py --mode generation --limit N
    uv run scripts/run_eval.py --mode generation --limit N --report-extended
    uv run scripts/run_eval.py --mode retrieval
    uv run scripts/run_eval.py --mode all --limit N
"""

import argparse
import asyncio
import contextlib
import datetime as dt
import itertools
import sys
import time
from collections.abc import Awaitable
from pathlib import Path

from leaseclear.core.config import settings
from leaseclear.db.connection import db_session, get_conn, use_database
from leaseclear.evals.generation.metrics import AggregateMetrics, aggregate_metrics
from leaseclear.evals.generation.pipeline import run_all
from leaseclear.evals.generation.report import render_metrics_md
from leaseclear.evals.golden.loader import load_golden_items
from leaseclear.evals.retrieval.pipeline import RetrievalEvalResult, evaluate_retrievers
from leaseclear.evals.retrieval.report import render_retrieval_md
from leaseclear.evals.summary import update_readme_evals

BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = BACKEND_DIR.parent
REPORTS_DIR = BACKEND_DIR / "src/leaseclear/evals/reports"
README_MD = REPO_ROOT / "README.md"

_SPINNER_FRAMES = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def _fmt_elapsed(seconds: float) -> str:
    mins, secs = divmod(int(seconds), 60)
    return f"{mins}:{secs:02d}" if mins else f"{secs}s"


async def _with_spinner[T](message: str, awaitable: Awaitable[T]) -> T:
    """Show a braille spinner with elapsed time while `awaitable` runs."""
    if not sys.stderr.isatty():
        return await awaitable

    stop = asyncio.Event()
    started = time.perf_counter()
    frames = itertools.cycle(_SPINNER_FRAMES)
    ok = False

    async def _spin() -> None:
        while not stop.is_set():
            elapsed = _fmt_elapsed(time.perf_counter() - started)
            frame = next(frames)
            sys.stderr.write(
                f"\r\033[36m{frame}\033[0m {message}  \033[2m{elapsed}\033[0m"
            )
            sys.stderr.flush()
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), timeout=0.08)
        sys.stderr.write("\r\033[K")
        elapsed = _fmt_elapsed(time.perf_counter() - started)
        mark = "\033[32m✔\033[0m" if ok else "\033[31m✖\033[0m"
        sys.stderr.write(f"{mark} {message}  \033[2m{elapsed}\033[0m\n")
        sys.stderr.flush()

    spinner_task = asyncio.create_task(_spin())
    try:
        result = await awaitable
        ok = True
        return result
    finally:
        stop.set()
        await spinner_task


async def _ensure_corpus_ingested() -> None:
    async with db_session():
        count = await get_conn().fetchval("SELECT count(*) FROM documents")
    if not count:
        raise SystemExit("No documents in the eval database.")


async def _run_generation(
    limit: int, *, report_extended: bool = False
) -> AggregateMetrics:
    items = load_golden_items(limit=limit)
    results = await _with_spinner(
        f"Running generation eval ({len(items)} items)",
        run_all(items),
    )
    metrics = aggregate_metrics(results)

    timestamp = dt.datetime.now(dt.UTC).strftime("%H%M%S-%Y%m%d")
    out_path = REPORTS_DIR / f"eval-generation-{timestamp}.md"
    out_path.write_text(
        render_metrics_md(metrics, results, report_extended=report_extended)
    )
    print(f"wrote {out_path}")

    for score in (
        metrics.retrieval_recall_at_8,
        metrics.faithfulness,
        metrics.citation_precision,
        metrics.refusal_accuracy,
        metrics.answer_match,
        metrics.hallucination_rate,
    ):
        print(f"{score.name}: {score.value} (target {score.target}, n={score.n})")

    return metrics


async def _run_retrieval(limit: int) -> RetrievalEvalResult:
    items = load_golden_items(limit=limit)
    result = await _with_spinner(
        f"Running retrieval eval ({len(items)} items)",
        evaluate_retrievers(items),
    )

    timestamp = dt.datetime.now(dt.UTC).strftime("%H%M%S-%Y%m%d")
    out_path = REPORTS_DIR / f"eval-retrieval-{timestamp}.md"
    report = render_retrieval_md(result)
    out_path.write_text(report)
    print(f"wrote {out_path}\n")
    print(report)
    return result


def _latest_report(prefix: str) -> Path | None:
    paths = sorted(
        REPORTS_DIR.glob(f"{prefix}-*.md"),
        key=lambda p: p.stat().st_mtime,
    )
    return paths[-1] if paths else None


def _write_readme_summary(
    *,
    generation_metrics: AggregateMetrics | None,
    retrieval_result: RetrievalEvalResult | None,
) -> None:
    update_readme_evals(
        README_MD,
        repo_root=REPO_ROOT,
        generation_report=_latest_report("eval-generation"),
        retrieval_report=_latest_report("eval-retrieval"),
        generation_metrics=generation_metrics,
        retrieval_result=retrieval_result,
    )
    print(f"updated {README_MD}")


async def main(mode: str, limit: int, *, report_extended: bool = False) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)

    generation_metrics: AggregateMetrics | None = None
    retrieval_result: RetrievalEvalResult | None = None

    async with use_database(settings.eval_database_url):
        await _ensure_corpus_ingested()

        if mode in ("generation", "all"):
            generation_metrics = await _run_generation(
                limit, report_extended=report_extended
            )
        if mode in ("retrieval", "all"):
            retrieval_result = await _run_retrieval(limit)

    _write_readme_summary(
        generation_metrics=generation_metrics,
        retrieval_result=retrieval_result,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["generation", "retrieval", "all"],
        default="generation",
    )
    parser.add_argument(
        "--limit",
        type=int,
        required=True,
        help="Random sample size per question type",
    )
    parser.add_argument(
        "--report-extended",
        action="store_true",
        help=(
            "Include the full generation user message (docs + clauses + question) "
            "in the generation report; default is question only"
        ),
    )
    args = parser.parse_args()
    asyncio.run(main(args.mode, args.limit, report_extended=args.report_extended))
