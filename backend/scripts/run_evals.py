import asyncio
from pathlib import Path

from leaseclear.db.connection import close_pool, db_session, get_conn
from leaseclear.evals.golden.loader import load_golden_items
from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.pipeline import run_all
from leaseclear.evals.report import render_metrics_md

METRICS_PATH = Path(__file__).resolve().parents[2] / "METRICS.md"


async def _ensure_corpus_ingested() -> None:
    async with db_session():
        count = await get_conn().fetchval("SELECT count(*) FROM documents")
    if not count:
        raise SystemExit(
            "No documents in the database. Run `uv run python scripts/ingest.py` "
            "against the corpus in corpus/generated first."
        )


async def main() -> None:
    items = load_golden_items()
    try:
        await _ensure_corpus_ingested()
        results = await run_all(items)
    finally:
        await close_pool()

    metrics = aggregate_metrics(results)
    METRICS_PATH.write_text(render_metrics_md(metrics, results))
    print(f"wrote {METRICS_PATH}")

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
