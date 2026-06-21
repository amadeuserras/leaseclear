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
class ParsedChunk(ChunkBase):
    pass


@dataclass
class EmbeddedChunk(ChunkBase):
    embedding: list[float]


@dataclass
class RetrievedChunk(ChunkBase):
    similarity: float
