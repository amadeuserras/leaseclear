import asyncio
import datetime as dt
from pathlib import Path

from leaseclear.core.config import settings
from leaseclear.db.connection import db_session, get_conn, use_database
from leaseclear.evals.golden.loader import load_golden_items
from leaseclear.evals.metrics import aggregate_metrics
from leaseclear.evals.pipeline import run_all
from leaseclear.evals.report import render_metrics_md

REPORTS_DIR = Path(__file__).resolve().parents[1] / "src/leaseclear/evals/reports"
LIMIT = 4


async def _ensure_corpus_ingested() -> None:
    async with db_session():
        count = await get_conn().fetchval("SELECT count(*) FROM documents")
    if not count:
        raise SystemExit("No documents in the eval database.")


async def main() -> None:
    items = load_golden_items(limit=LIMIT)

    async with use_database(settings.eval_database_url):
        await _ensure_corpus_ingested()
        results = await run_all(items)

    metrics = aggregate_metrics(results)

    REPORTS_DIR.mkdir(exist_ok=True)
    timestamp = dt.datetime.now(dt.UTC).strftime("%H%M%S-%Y%m%d")
    out_path = REPORTS_DIR / f"eval-{timestamp}.md"
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


if __name__ == "__main__":
    asyncio.run(main())
