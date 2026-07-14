from __future__ import annotations

import re

from leaseclear.types import ChunkBase, Citation, GenerationResult

# Matches inline citation ids as they appear in answers and chunk prefixes.
CITATION_ID_RE = re.compile(r"\[([a-z0-9-]+) (§[^\]]+|p\d+(?:\(\d+\))?)\]")


def extract_citation_ids(text: str) -> list[str]:
    """Distinct citation ids in reading order, taken from inline markers."""
    ids: list[str] = []
    seen: set[str] = set()
    for match in CITATION_ID_RE.finditer(text):
        citation_id = match.group(0)
        if citation_id not in seen:
            seen.add(citation_id)
            ids.append(citation_id)
    return ids


def generation_result_from_answer(answer: str) -> GenerationResult:
    answer = answer.strip()
    return GenerationResult(
        answer=answer,
        citations=[Citation(id=cid) for cid in extract_citation_ids(answer)],
    )


def resolve_citations(
    citation_ids: list[str], chunks: list[ChunkBase]
) -> list[ChunkBase]:
    by_citation = {chunk.citation_id: chunk for chunk in chunks}
    return [by_citation[cid] for cid in citation_ids if cid in by_citation]
