from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from slugify import slugify

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
    document_slug: str | None
    clause_label: str | None
    page_number: int | None

    @property
    def canonical_document_slug(self) -> str | None:
        if self.document_slug is None:
            return None
        return slugify(self.document_slug)

    @property
    def clause_number(self) -> str | None:
        if self.clause_label is None:
            return None
        m = re.compile(r"^(\d+(?:\.\d+)?)\.").match(self.clause_label)
        return m.group(1) if m else None


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
                document_slug=data.get("document_slug"),
                clause_label=data.get("clause_label"),
                page_number=data.get("page_number"),
            )
        )
    return items


def load_golden_items(
    paths: tuple[Path, ...] = DEFAULT_GOLDEN_PATHS, *, limit: int | None = None
) -> list[GoldenItem]:
    items: list[GoldenItem] = []
    for path in paths:
        items.extend(_load_golden_file(path))
    return items[:limit] if limit is not None else items
