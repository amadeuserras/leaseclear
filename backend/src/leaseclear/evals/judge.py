from __future__ import annotations

import json

from openai import AsyncOpenAI

from leaseclear.core.config import settings
from leaseclear.evals.types import ClaimJudgment, JudgeVerdict
from leaseclear.types import ChunkBase
from leaseclear.utils.text import strip_markdown_fence

JUDGE_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are a strict fact-checking judge for a residential lease Q&A system. You
did not write the answer below - your job is to check it against source text.

You will receive:
- QUESTION: the user's question
- ANSWER: the system's answer, with inline citation ids like [doc §3]
- CITED CLAUSES: the full text of every clause the answer cited
- RETRIEVED CLAUSES: the full text of every clause the system had available,
  a superset of CITED CLAUSES

Break the answer into its atomic factual claims (ignore hedging language and
the refusal sentence itself, if present). For each claim, report:
- "text": the claim, verbatim or close to it
- "cited_ids": the citation ids attached to that claim in the answer text
  (empty list if the claim carries no citation)
- "supported_by_citation": true only if the CITED CLAUSES text for this
  claim's cited_ids actually states the fact; false if unsupported or if
  cited_ids is empty
- "supported_by_context": true if ANY clause in RETRIEVED CLAUSES supports
  the fact stated, whether cited or not

Respond with JSON only, no prose, no markdown fences, in this exact shape:
{"claims": [{"text": "...", "cited_ids": ["[doc §3]"],
"supported_by_citation": true, "supported_by_context": true}]}

If the answer makes no factual claims (e.g. it is a refusal), return
{"claims": []}.
""".strip()


def _build_user_message(
    question: str,
    answer: str,
    cited: list[ChunkBase],
    retrieved: list[ChunkBase],
) -> str:
    cited_block = "\n\n".join(f"{c.citation_id}\n{c.text}" for c in cited) or "(none)"
    retrieved_block = "\n\n".join(f"{c.citation_id}\n{c.text}" for c in retrieved)
    return (
        f"QUESTION: {question}\n\n"
        f"ANSWER:\n{answer}\n\n"
        f"CITED CLAUSES:\n{cited_block}\n\n"
        f"RETRIEVED CLAUSES:\n{retrieved_block}"
    )


def _parse_verdict(raw: str) -> JudgeVerdict:
    try:
        data = json.loads(strip_markdown_fence(raw))
    except json.JSONDecodeError as e:
        raise ValueError(f"Judge returned invalid JSON: {e}\n\nRaw:\n{raw}") from e

    claims = [
        ClaimJudgment(
            text=claim["text"],
            cited_ids=list(claim.get("cited_ids", [])),
            supported_by_citation=bool(claim["supported_by_citation"]),
            supported_by_context=bool(claim["supported_by_context"]),
        )
        for claim in data.get("claims", [])
    ]
    return JudgeVerdict(claims=claims)


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_judge_api_key)


async def judge_answer(
    question: str,
    answer: str,
    cited: list[ChunkBase],
    retrieved: list[ChunkBase],
) -> JudgeVerdict:
    client = _get_client()
    response = await client.chat.completions.create(
        model=JUDGE_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_message(question, answer, cited, retrieved),
            },
        ],
    )
    raw = response.choices[0].message.content or "{}"
    return _parse_verdict(raw)
