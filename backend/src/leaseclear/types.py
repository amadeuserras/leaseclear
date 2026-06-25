from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class ChunkBase:
    chunk_id: str
    document_id: str
    text: str
    clause_label: str | None
    page_number: int
    char_start: int
    char_end: int
    token_count: int


@dataclass
class EmbeddedChunk(ChunkBase):
    embedding: list[float]


@dataclass
class LabelledChunk:
    citation_id: str
    chunk_id: str
    text: str


@dataclass
class Citation:
    id: str
    quote: str


@dataclass
class GenerationResult:
    answer: str
    citations: list[Citation]
    confidence: float


@dataclass
class ValidationResult:
    passed: bool
    phantom_ids: list[str]
    uncited_claims: bool


@dataclass
class GenerationStreamMeta:
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass
class QueryLogEntry:
    id: UUID
    question: str
    document_ids: list[str] | None
    chunk_ids_retrieved: list[str]
    ttft_s: float | None
    total_s: float | None
    input_tokens: int | None
    output_tokens: int | None
    refused: bool
