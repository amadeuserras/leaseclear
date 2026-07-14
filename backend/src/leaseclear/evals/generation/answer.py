from __future__ import annotations

import re

from leaseclear.generation.generate import REFUSAL_MESSAGE
from leaseclear.types import ChunkBase, Citation, GenerationResult, ValidationResult

# Matches inline citation ids as they appear in answers.
CITATION_ID_RE = re.compile(r"\[([a-z0-9-]+) (§[^\]]+|p\d+(?:\(\d+\))?)\]")


def extract_citation_ids(text: str) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for match in CITATION_ID_RE.finditer(text):
        citation_id = match.group(0)
        if citation_id not in seen:
            seen.add(citation_id)
            ids.append(citation_id)
    return ids


def result_from_answer(answer: str) -> GenerationResult:
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


def is_refusal(result: GenerationResult) -> bool:
    return REFUSAL_MESSAGE in result.answer and not result.citations


def validate(result: GenerationResult, chunks: list[ChunkBase]) -> ValidationResult:
    if is_refusal(result):
        return ValidationResult(passed=True, phantom_ids=[], uncited_claims=False)

    valid_ids = {c.citation_id for c in chunks}
    phantom_ids = [c.id for c in result.citations if c.id not in valid_ids]
    uncited_claims = not result.citations and bool(result.answer.strip())
    passed = not phantom_ids and not uncited_claims

    return ValidationResult(
        passed=passed,
        phantom_ids=phantom_ids,
        uncited_claims=uncited_claims,
    )
