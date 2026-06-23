from __future__ import annotations

from leaseclear.api.schemas import Citation, QueryResponse
from leaseclear.db.connection import get_pool
from leaseclear.generation.generate import generate
from leaseclear.generation.label import label_chunks
from leaseclear.retrieval import hybrid
from leaseclear.types import ChunkBase, GenerationResult, LabelledChunk


def _to_response(
    result: GenerationResult,
    retrieved: list[ChunkBase],
    labelled: list[LabelledChunk],
) -> QueryResponse:
    chunk_by_citation = {
        label.citation_id: chunk
        for label, chunk in zip(labelled, retrieved, strict=True)
    }
    citations = [
        Citation(
            chunk_id=chunk.chunk_id,
            clause_label=chunk.clause_label or "",
            page_number=chunk.page_number,
            passage=c.quote,
        )
        for c in result.citations
        if (chunk := chunk_by_citation.get(c.id)) is not None
    ]
    return QueryResponse(
        answer=result.answer,
        citations=citations,
        confidence=result.confidence,
    )


async def run_query(
    question: str,
    document_ids: list[str] | None = None,
) -> QueryResponse:
    pool = await get_pool()
    async with pool.acquire() as conn:
        retrieved = await hybrid.search(conn, question)

    if document_ids is not None:
        retrieved = [c for c in retrieved if c.document_id in document_ids]

    labelled = label_chunks(retrieved)
    result = generate(question, labelled)
    return _to_response(result, retrieved, labelled)
