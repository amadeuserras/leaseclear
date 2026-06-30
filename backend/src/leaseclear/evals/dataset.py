from __future__ import annotations

import json
from pathlib import Path

from leaseclear.evals.types import GoldenItem

GOLDEN_PATH = Path(__file__).resolve().parent / "golden" / "golden.jsonl"


def load_all_golden(limit: int | None = None) -> list[GoldenItem]:
    items: list[GoldenItem] = []
    for line_no, line in enumerate(GOLDEN_PATH.read_text().splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            items.append(GoldenItem(**json.loads(stripped)))
        except (json.JSONDecodeError, TypeError, KeyError) as e:
            raise ValueError(f"{GOLDEN_PATH}:{line_no}: {e}") from e
        if limit is not None and len(items) >= limit:
            break
    return items
