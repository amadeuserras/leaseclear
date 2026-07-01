from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from leaseclear.db.connection import close_pool, db_session
from leaseclear.evals.dataset import load_all_golden
from leaseclear.evals.judge import judge
from leaseclear.evals.metrics import aggregate, score
from leaseclear.evals.report import format_report, result_path, write_report
from leaseclear.evals.runner import run_item
from leaseclear.evals.types import EvalResult, GoldenItem


async def run_eval(
    *,
    items: list[GoldenItem] | None = None,
    use_judge: bool = True,
    include_cases: bool = True,
    output_path: Path | None = None,
) -> tuple[list[EvalResult], Path]:
    golden = items if items is not None else load_all_golden()
    results: list[EvalResult] = []

    async with db_session():
        for item in golden:
            result = await run_item(item)
            score(result)
            if use_judge:
                result.faithfulness, result.citation_precision = await judge(result)
            results.append(result)

    path = output_path or result_path()
    metrics = aggregate(results)
    write_report(metrics, results, path, include_cases=include_cases)
    return results, path


async def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the LeaseClear eval suite.")
    parser.add_argument("--no-judge", action="store_true")
    parser.add_argument("--no-cases", action="store_true")
    args = parser.parse_args(argv)

    include_cases = not args.no_cases
    try:
        results, path = await run_eval(
            use_judge=not args.no_judge,
            include_cases=include_cases,
        )
    finally:
        await close_pool()

    metrics = aggregate(results)
    print(format_report(metrics, results, include_cases=include_cases))
    print(f"\nWrote {path}")


if __name__ == "__main__":
    asyncio.run(main())
