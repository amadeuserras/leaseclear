from __future__ import annotations

from leaseclear.types import LabelledChunk, RetrievedChunk


def _make_citation_id(chunk: RetrievedChunk) -> str:
    if chunk.clause_label:
        return f"[{chunk.document_id} §{chunk.clause_label}]"
    return f"[{chunk.document_id} p.{chunk.page_number}]"


def label_chunks(chunks: list[RetrievedChunk]) -> list[LabelledChunk]:
    return [
        LabelledChunk(
            citation_id=_make_citation_id(c),
            chunk_id=c.chunk_id,
            text=c.text,
            similarity=c.similarity,
        )
        for c in chunks
    ]
