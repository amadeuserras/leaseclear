from __future__ import annotations

import asyncio
import time

from leaseclear.db.connection import db_session
from leaseclear.evals import judge as judge_module
from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.evals.retrieval_recall import check_recall
from leaseclear.evals.types import CaseResult
from leaseclear.generation.generate import generate_stream
from leaseclear.generation.parse import parse_response, resolve_citations
from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.generation.validate import validate
from leaseclear.retrieval import hybrid
from leaseclear.types import ChunkBase, Citation, GenerationResult, GenerationStreamMeta

# Small cap on in-flight cases so a growing golden set doesn't fan out into an
# API rate-limit storm, while still being faster than fully sequential.
MAX_CONCURRENT_CASES = 4


async def _generate(
    question: str, chunks: list[ChunkBase]
) -> tuple[GenerationResult, GenerationStreamMeta, float | None, float]:
    start = time.perf_counter()
    ttft_s: float | None = None
    raw_parts: list[str] = []

    tokens, meta = generate_stream(question, chunks)
    async for token in tokens:
        if ttft_s is None:
            ttft_s = time.perf_counter() - start
        raw_parts.append(token)

    prose, citation_ids, confidence = parse_response("".join(raw_parts))
    result = GenerationResult(
        answer=prose,
        citations=[Citation(id=cid) for cid in citation_ids],
        confidence=confidence,
    )
    return result, meta, ttft_s, time.perf_counter() - start


async def run_case(item: GoldenItem) -> CaseResult:
    try:
        async with db_session():
            retrieved = await hybrid.search(item.question)

        retrieval_hit = check_recall(item, retrieved)
        result, meta, ttft_s, total_s = await _generate(item.question, retrieved)
        validation = validate(result, retrieved, REFUSAL_MESSAGE)
        refused = result.answer.strip() == REFUSAL_MESSAGE
        correctly_refused = refused == item.expected_refusal

        verdict = None
        if not refused and result.answer.strip():
            cited = resolve_citations([c.id for c in result.citations], retrieved)
            verdict = await judge_module.judge_answer(
                item.question, result.answer, cited, retrieved
            )

        return CaseResult(
            item_id=item.id,
            item_type=item.type,
            question=item.question,
            retrieved=retrieved,
            retrieval_hit=retrieval_hit,
            result=result,
            validation=validation,
            refused=refused,
            expected_refusal=item.expected_refusal,
            correctly_refused=correctly_refused,
            judge=verdict,
            ttft_s=ttft_s,
            total_s=total_s,
            input_tokens=meta.input_tokens,
            output_tokens=meta.output_tokens,
        )
    except Exception as e:  # noqa: BLE001 - a broken case must not sink the run
        return CaseResult(
            item_id=item.id,
            item_type=item.type,
            question=item.question,
            retrieved=[],
            retrieval_hit=None,
            result=GenerationResult(answer="", citations=[], confidence=0.0),
            validation=validate(
                GenerationResult(answer="", citations=[], confidence=0.0),
                [],
                REFUSAL_MESSAGE,
            ),
            refused=False,
            expected_refusal=item.expected_refusal,
            correctly_refused=False,
            judge=None,
            ttft_s=None,
            total_s=0.0,
            input_tokens=None,
            output_tokens=None,
            error=str(e),
        )


async def run_all(items: list[GoldenItem]) -> list[CaseResult]:
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_CASES)

    async def _bounded(item: GoldenItem) -> CaseResult:
        async with semaphore:
            return await run_case(item)

    return list(await asyncio.gather(*(_bounded(item) for item in items)))
