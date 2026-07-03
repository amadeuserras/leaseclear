import argparse
import asyncio
import datetime as dt
from pathlib import Path

from leaseclear.db.connection import close_pool, db_session, get_conn
from leaseclear.evals.golden.loader import load_golden_items
from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.pipeline import run_all
from leaseclear.evals.report import render_metrics_md

REPORTS_DIR = Path(__file__).resolve().parents[1] / "src/leaseclear/evals/reports"
LIMIT = 10


async def _ensure_corpus_ingested() -> None:
    async with db_session():
        count = await get_conn().fetchval("SELECT count(*) FROM documents")
    if not count:
        raise SystemExit(
            "No documents in the database. Run `uv run python scripts/ingest.py` "
            "against the corpus in corpus/generated first."
        )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="only run the first N golden items (for quick, cheap dev runs)",
    )
    return parser.parse_args()


async def main() -> None:
    args = _parse_args()
    items = load_golden_items(limit=LIMIT)
    if args.limit is not None:
        items = items[: args.limit]

    try:
        await _ensure_corpus_ingested()
        results = await run_all(items)
    finally:
        await close_pool()

    metrics = aggregate_metrics(results)

    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = dt.datetime.now(dt.UTC).strftime("%Y%m%d-%H%M%S")
    out_path = REPORTS_DIR / f"{timestamp}.md"
    out_path.write_text(render_metrics_md(metrics, results))
    print(f"wrote {out_path}")

    for score in (
        metrics.retrieval_recall_at_8,
        metrics.faithfulness,
        metrics.citation_precision,
        metrics.refusal_accuracy,
        metrics.hallucination_rate,
    ):
        print(f"{score.name}: {score.value} (target {score.target}, n={score.n})")


if __name__ == "__main__":
    asyncio.run(main())
