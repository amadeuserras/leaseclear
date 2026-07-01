from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from slugify import slugify

GoldenType = Literal["answerable", "unanswerable", "hard"]

DEFAULT_GOLDEN_PATH = Path(__file__).with_name("golden.jsonl")


@dataclass(frozen=True)
class GoldenItem:
    id: str
    type: GoldenType
    question: str
    expected_answer: str | None
    expected_refusal: bool
    document_slug: str | None
    clause_number: str | None
    page_number: int | None

    @property
    def canonical_document_slug(self) -> str | None:
        """The slug as it will appear on stored chunks.

        golden.jsonl slugs are written by hand from case filenames (which use
        underscores, e.g. "texas-washington_price"); ingestion runs every
        filename through `slugify`, which turns underscores into hyphens. Both
        sides must be normalized the same way before comparing.
        """
        if self.document_slug is None:
            return None
        return slugify(self.document_slug)


def load_golden_items(path: Path = DEFAULT_GOLDEN_PATH) -> list[GoldenItem]:
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
                clause_number=data.get("clause_number"),
                page_number=data.get("page_number"),
            )
        )
    return items
