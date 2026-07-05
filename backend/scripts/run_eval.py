"""Eval runner.

Usage:
    uv run scripts/run_eval.py --mode generation --limit N  # --limit required
    uv run scripts/run_eval.py --mode retrieval
    uv run scripts/run_eval.py --mode all --limit N          # --limit required
"""

import argparse
import asyncio
import datetime as dt
from pathlib import Path

from leaseclear.core.config import settings
from leaseclear.db.connection import db_session, get_conn, use_database
from leaseclear.evals.generation.metrics import aggregate_metrics
from leaseclear.evals.generation.pipeline import run_all
from leaseclear.evals.generation.report import render_metrics_md
from leaseclear.evals.golden.loader import load_golden_items
from leaseclear.evals.retrieval.pipeline import evaluate_retrievers
from leaseclear.evals.retrieval.report import render_retrieval_md

REPORTS_DIR = Path(__file__).resolve().parents[1] / "src/leaseclear/evals/reports"


async def _ensure_corpus_ingested() -> None:
    async with db_session():
        count = await get_conn().fetchval("SELECT count(*) FROM documents")
    if not count:
        raise SystemExit("No documents in the eval database.")


async def _run_generation(limit: int | None) -> None:
    items = load_golden_items(limit=limit)
    results = await run_all(items)
    metrics = aggregate_metrics(results)

    timestamp = dt.datetime.now(dt.UTC).strftime("%H%M%S-%Y%m%d")
    out_path = REPORTS_DIR / f"eval-generation-{timestamp}.md"
    out_path.write_text(render_metrics_md(metrics, results))
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


async def _run_retrieval() -> None:
    items = load_golden_items()
    result = await evaluate_retrievers(items)

    timestamp = dt.datetime.now(dt.UTC).strftime("%H%M%S-%Y%m%d")
    out_path = REPORTS_DIR / f"eval-retrieval-{timestamp}.md"
    report = render_retrieval_md(result)
    out_path.write_text(report)
    print(f"wrote {out_path}\n")
    print(report)


async def main(mode: str, limit: int | None) -> None:
    REPORTS_DIR.mkdir(exist_ok=True)

    async with use_database(settings.eval_database_url):
        await _ensure_corpus_ingested()

        if mode in ("generation", "all"):
            await _run_generation(limit)
        if mode in ("retrieval", "all"):
            await _run_retrieval()


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
        default=None,
        help="Items to run (required for --mode generation|all)",
    )
    args = parser.parse_args()
    if args.mode in ("generation", "all") and args.limit is None:
        parser.error("--limit is required when running the generation eval")
    asyncio.run(main(args.mode, args.limit))
