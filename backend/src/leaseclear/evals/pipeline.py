from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from leaseclear.db.connection import close_pool, db_session
from leaseclear.evals.dataset import load_all_golden
from leaseclear.evals.judge import judge
from leaseclear.evals.metrics import aggregate, score
from leaseclear.evals.report import DEFAULT_EVAL_PATH, format_report, write_report
from leaseclear.evals.runner import run_item
from leaseclear.evals.types import EvalResult, GoldenItem

logger = logging.getLogger(__name__)


async def run_eval(
    *,
    items: list[GoldenItem] | None = None,
    use_judge: bool = True,
    eval_path: Path = DEFAULT_EVAL_PATH,
    include_cases: bool = False,
) -> list[EvalResult]:
    golden = items if items is not None else load_all_golden()
    results: list[EvalResult] = []

    async with db_session():
        for item in golden:
            logger.info("eval: %s", item.id)
            result = await run_item(item)
            score(result)

            if use_judge:
                result.faithfulness, result.citation_precision = await judge(result)

            results.append(result)

    metrics = aggregate(results)
    write_report(metrics, results, eval_path, include_cases=include_cases)
    return results


async def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the LeaseClear eval suite.")
    parser.add_argument("--no-judge", action="store_true")
    parser.add_argument("--eval", type=Path, default=DEFAULT_EVAL_PATH)
    parser.add_argument("--cases", action="store_true")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(levelname)s %(message)s",
    )

    try:
        results = await run_eval(
            use_judge=not args.no_judge,
            eval_path=args.eval,
            include_cases=args.cases,
        )
    finally:
        await close_pool()

    metrics = aggregate(results)
    print(format_report(metrics, results, include_cases=args.cases))
    print(f"\nWrote {args.eval}")


if __name__ == "__main__":
    asyncio.run(main())
