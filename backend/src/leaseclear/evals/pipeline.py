from __future__ import annotations

import asyncio
import time

from leaseclear.db.connection import db_session
from leaseclear.evals import answer_match as answer_match_module
from leaseclear.evals import judge as judge_module
from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.evals.retrieval_recall import check_recall
from leaseclear.evals.types import CaseResult
from leaseclear.filtering.documents import list_document_metadata
from leaseclear.filtering.filter import filter_documents
from leaseclear.generation.generate import generate_stream
from leaseclear.generation.parse import parse_response, resolve_citations
from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.generation.validate import is_refusal, validate
from leaseclear.retrieval import hybrid
from leaseclear.types import (
    ChunkBase,
    Citation,
    DocumentMetadata,
    GenerationResult,
    GenerationStreamMeta,
    ParsedResponse,
)

MAX_CONCURRENT_CASES = 4


async def _generate(
    question: str, chunks: list[ChunkBase], documents: list[DocumentMetadata]
) -> tuple[GenerationResult, GenerationStreamMeta, float | None, float]:
    start = time.perf_counter()
    ttft_s: float | None = None
    raw_parts: list[str] = []

    tokens, meta = generate_stream(question, chunks, documents)
    async for token in tokens:
        if ttft_s is None:
            ttft_s = time.perf_counter() - start
        raw_parts.append(token)

    parsed: ParsedResponse = parse_response("".join(raw_parts))
    result = GenerationResult(
        answer=parsed.prose,
        citations=[Citation(id=cid) for cid in parsed.citation_ids],
    )
    return result, meta, ttft_s, time.perf_counter() - start


async def run_case(item: GoldenItem) -> CaseResult:
    try:
        async with db_session():
            document_ids = await filter_documents(item.question)
            retrieved = await hybrid.search(item.question, document_ids=document_ids)
            documents = await list_document_metadata(document_ids)

        retrieval_hit = check_recall(item, retrieved)
        result, meta, ttft_s, total_s = await _generate(
            item.question, retrieved, documents
        )
        validation = validate(result, retrieved, REFUSAL_MESSAGE)
        refused = is_refusal(result, REFUSAL_MESSAGE)

        verdict = None
        matched = None
        if not refused and result.answer.strip():
            cited = resolve_citations([c.id for c in result.citations], retrieved)
            verdict = await judge_module.judge_answer(
                item.question, result.answer, cited, retrieved
            )
        if item.expected_answer is not None and not refused:
            matched = await answer_match_module.check_answer_match(
                item.question, result.answer, item.expected_answer
            )

        return CaseResult(
            item_id=item.id,
            item_type=item.type,
            question=item.question,
            retrieved=retrieved,
            documents=documents,
            retrieval_hit=retrieval_hit,
            result=result,
            validation=validation,
            refused=refused,
            expected_refusal=item.expected_refusal,
            expected_answer=item.expected_answer,
            answer_match=matched,
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
            documents=[],
            retrieval_hit=None,
            result=GenerationResult(answer="", citations=[]),
            validation=validate(
                GenerationResult(answer="", citations=[]),
                [],
                REFUSAL_MESSAGE,
            ),
            refused=False,
            expected_refusal=item.expected_refusal,
            expected_answer=item.expected_answer,
            answer_match=None,
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
