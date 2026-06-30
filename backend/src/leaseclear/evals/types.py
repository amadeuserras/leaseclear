from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from leaseclear.types import ChunkBase

GoldenType = Literal["answerable", "unanswerable", "hard"]


@dataclass(frozen=True)
class GoldenItem:
    id: str
    type: GoldenType
    question: str
    document_slug: str
    expected_answer: str | None = None
    expected_refusal: bool = False
    clause_label: str | None = None
    page_number: int | None = None


@dataclass
class EvalResult:
    item: GoldenItem
    answer: str
    confidence: float
    refused: bool
    retrieved_chunks: list[ChunkBase]
    cited_chunks: list[ChunkBase]
    validation_passed: bool
    retrieval_recall: float = 0.0
    refusal_accuracy: float = 0.0
    answer_match: float = 0.0
    faithfulness: float | None = None
    citation_precision: float | None = None


@dataclass(frozen=True)
class AggregateMetrics:
    count: int
    retrieval_recall: float
    refusal_accuracy: float
    answer_match: float
    faithfulness: float | None
    citation_precision: float | None
