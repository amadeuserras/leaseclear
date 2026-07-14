from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

GoldenType = Literal["answerable", "unanswerable", "hard"]

GOLDEN_DIR = Path(__file__).parent
DEFAULT_GOLDEN_PATHS = (
    GOLDEN_DIR / "answerable.jsonl",
    GOLDEN_DIR / "unanswerable.jsonl",
    GOLDEN_DIR / "hard.jsonl",
)


@dataclass(frozen=True)
class GoldenItem:
    id: str
    type: GoldenType
    question: str
    expected_answer: str | None
    expected_refusal: bool
    citation_ids: list[str] = field(default_factory=list)


def _load_golden_file(path: Path) -> list[GoldenItem]:
    items: list[GoldenItem] = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        data = json.loads(line)
        items.append(
            GoldenItem(
                id=data["id"],
                type=data["type"],
                question=data["question"],
                expected_answer=data.get("expected_answer"),
                expected_refusal=data["expected_refusal"],
                citation_ids=data.get("citation_ids", []),
            )
        )
    return items


def load_golden_items(
    paths: tuple[Path, ...] = DEFAULT_GOLDEN_PATHS, *, limit: int | None = None
) -> list[GoldenItem]:
    items: list[GoldenItem] = []
    for path in paths:
        file_items = _load_golden_file(path)
        items.extend(file_items[:limit] if limit is not None else file_items)
    return items
