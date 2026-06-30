from __future__ import annotations

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


async def _judge_citation(
    client: AsyncOpenAI, question: str, answer: str, chunk: ChunkBase
) -> bool:
    return await _ask_yes_no(
        client,
        system=(
            "You grade lease citations. Decide whether the cited passage "
            "supports the answer to the question. Reply YES or NO only."
        ),
        user=(
            f"Question: {question}\n\n"
            f"Answer: {answer}\n\n"
            f"Cited passage ({chunk.clause_label or 'unknown'}, "
            f"p.{chunk.page_number}):\n"
            f"{chunk.text}\n\n"
            "Does this citation support the answer?"
        ),
    )


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
        verdicts = [
            await _judge_citation(client, result.item.question, result.answer, chunk)
            for chunk in result.cited_chunks
        ]
        citation_precision = sum(verdicts) / len(verdicts)

    return faithfulness_score, citation_precision
