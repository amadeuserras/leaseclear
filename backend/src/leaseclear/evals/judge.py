from __future__ import annotations

import json

from openai import AsyncOpenAI

from leaseclear.core.config import settings
from leaseclear.evals.types import EvalResult
from leaseclear.types import ChunkBase

MODEL = "gpt-4o-mini"


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_judge_api_key)


async def _ask_yes_no(client: AsyncOpenAI, system: str, user: str) -> bool:
    response = await client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )
    text = response.choices[0].message.content or ""
    return text.strip().casefold().startswith("y")


async def _judge_faithfulness(
    client: AsyncOpenAI, question: str, answer: str, passages: list[str]
) -> bool:
    joined = "\n---\n".join(passages)
    return await _ask_yes_no(
        client,
        system=(
            "You grade lease Q&A answers. Given lease passages and an answer, "
            "decide whether every factual claim in the answer is supported by "
            "the passages. Reply YES or NO only."
        ),
        user=(
            f"Question: {question}\n\n"
            f"Passages:\n{joined}\n\n"
            f"Answer: {answer}\n\n"
            "Is the answer fully supported?"
        ),
    )


async def _judge_citations(
    client: AsyncOpenAI, question: str, answer: str, chunks: list[ChunkBase]
) -> list[bool]:
    """Judge all citations in one call, with the full answer and every cited
    passage visible together. This lets a citation be marked valid when it
    provides supporting/contextual grounding for a claim alongside the other
    cited passages, rather than requiring each passage to prove the entire
    answer in isolation."""
    passages = "\n\n".join(
        f"[{i}] {chunk.clause_label or 'unknown'} "
        f"(p.{chunk.page_number}):\n{chunk.text}"
        for i, chunk in enumerate(chunks)
    )
    response = await client.chat.completions.create(
        model=MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You grade lease citations. You are given a question, an "
                    "answer that cites one or more numbered lease passages, and "
                    "the full text of each cited passage. For each passage, "
                    "decide whether it is an accurate, non-misleading source for "
                    "the specific claim it is cited for -- either directly, or "
                    "by providing supporting/contextual grounding together with "
                    "the other cited passages. Mark it invalid only if it is "
                    "irrelevant, contradicts the answer, or is fabricated. "
                    'Respond with JSON: {"verdicts": [true, false, ...]}, one '
                    "boolean per passage in the given order."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Answer: {answer}\n\n"
                    f"Cited passages:\n{passages}"
                ),
            },
        ],
    )
    text = response.choices[0].message.content or "{}"
    try:
        verdicts = json.loads(text).get("verdicts", [])
    except json.JSONDecodeError:
        verdicts = []
    verdicts = [bool(v) for v in verdicts][: len(chunks)]
    if len(verdicts) < len(chunks):
        verdicts += [False] * (len(chunks) - len(verdicts))
    return verdicts


async def judge(result: EvalResult) -> tuple[float, float]:
    """Return (faithfulness_score, citation_precision_score)."""
    if result.refused:
        return 1.0, 1.0

    client = _get_client()
    passages = [chunk.text for chunk in result.cited_chunks]

    if passages:
        faithful = await _judge_faithfulness(
            client, result.item.question, result.answer, passages
        )
        faithfulness_score = 1.0 if faithful else 0.0
    else:
        faithfulness_score = 0.0

    if not result.cited_chunks:
        citation_precision = 0.0
    else:
        verdicts = await _judge_citations(
            client, result.item.question, result.answer, result.cited_chunks
        )
        citation_precision = sum(verdicts) / len(verdicts)

    return faithfulness_score, citation_precision
