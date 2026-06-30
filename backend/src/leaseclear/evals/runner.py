from __future__ import annotations

from leaseclear.db.connection import DbConnection
from leaseclear.evals.types import EvalResult, GoldenItem
from leaseclear.generation.generate import generate_stream
from leaseclear.generation.parse import parse_response, resolve_citations
from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.generation.validate import validate
from leaseclear.retrieval import hybrid
from leaseclear.types import Citation, GenerationResult


async def run_item(conn: DbConnection, item: GoldenItem) -> EvalResult:
    retrieved = await hybrid.search(conn, item.question)

    raw_parts: list[str] = []
    tokens, _ = generate_stream(item.question, retrieved)
    async for token in tokens:
        raw_parts.append(token)

    prose, citation_ids, confidence = parse_response("".join(raw_parts))
    cited = resolve_citations(citation_ids, retrieved)

    result = GenerationResult(
        answer=prose,
        citations=[Citation(id=cid) for cid in citation_ids],
        confidence=confidence,
    )
    validation = validate(result, retrieved, REFUSAL_MESSAGE)

    return EvalResult(
        item=item,
        answer=prose,
        confidence=confidence,
        refused=prose.strip() == REFUSAL_MESSAGE,
        retrieved_chunks=retrieved,
        cited_chunks=cited,
        validation_passed=validation.passed,
    )
