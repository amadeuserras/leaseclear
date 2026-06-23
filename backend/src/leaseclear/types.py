from __future__ import annotations

from dataclasses import dataclass


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
    refusal: bool


@dataclass
class ValidationResult:
    passed: bool
    phantom_ids: list[str]
    uncited_claims: bool
