from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID


@dataclass
class UploadDocument:
    path: str
    filename: str


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class ParsedDocument:
    filename: str
    pages: list[PageText]


@dataclass
class AssignedDocument:
    id: UUID
    slug: str
    filename: str
    pages: list[PageText]


@dataclass
class EnrichedDocument(AssignedDocument):
    landlord_name: str | None
    tenant_names: list[str]
    property_address: str | None


@dataclass
class DocumentMetadata:
    id: UUID
    slug: str
    landlord_name: str | None
    tenant_names: list[str]
    property_address: str | None
    filename: str = ""


@dataclass
class ChunkBase:
    id: UUID
    document_id: UUID
    document_slug: str
    text: str
    clause_number: str | None
    clause_title: str | None
    start_page: int
    end_page: int
    index: int
    citation: str

    @property
    def citation_id(self) -> str:
        return f"[{self.document_slug} {self.citation}]"


@dataclass
class EmbeddedChunk(ChunkBase):
    embedding: list[float]


@dataclass
class Citation:
    id: str


@dataclass
class GenerationResult:
    answer: str
    citations: list[Citation]


@dataclass(frozen=True)
class ParsedResponse:
    prose: str
    citation_ids: list[str]


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
    user_id: UUID | None
    question: str
    document_ids: list[UUID] | None
    chunk_ids_retrieved: list[UUID]
    ttft_s: float | None
    total_s: float | None
    input_tokens: int | None
    output_tokens: int | None
    refused: bool
