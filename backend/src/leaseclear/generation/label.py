from __future__ import annotations

from leaseclear.types import ChunkBase, LabelledChunk


def _make_citation_id(chunk: ChunkBase) -> str:
    if chunk.clause_label:
        return f"[{chunk.document_id} §{chunk.clause_label}]"
    return f"[{chunk.document_id} p.{chunk.page_number}]"


def label_chunks(chunks: list[ChunkBase]) -> list[LabelledChunk]:
    return [
        LabelledChunk(
            citation_id=_make_citation_id(c),
            id=c.id,
            text=c.text,
        )
        for c in chunks
    ]
