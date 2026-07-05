from __future__ import annotations

import json

from openai import AsyncOpenAI

from leaseclear.core.config import settings
from leaseclear.utils.text import strip_markdown_fence

MATCH_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """
You are evaluating a residential lease Q&A system. You will receive:
- QUESTION: the user's question
- GENERATED_ANSWER: the system's answer, which may include inline citation ids
  like [doc §3]
- GOLDEN_ANSWER: the reference answer that correctly addresses the question

Decide whether the GENERATED_ANSWER essentially conveys the same substantive
answer as the GOLDEN_ANSWER. Ignore citation ids, formatting, and minor
wording differences when the core facts match. Extra correct detail in the
generated answer is fine.

Return false if the generated answer contradicts the golden answer, omits a
critical fact from the golden answer, or gives a materially different answer.

Respond with JSON only, no prose, no markdown fences, in this exact shape:
{"matches": true}
""".strip()


def _build_user_message(
    question: str, generated_answer: str, golden_answer: str
) -> str:
    return (
        f"QUESTION: {question}\n\n"
        f"GENERATED_ANSWER:\n{generated_answer}\n\n"
        f"GOLDEN_ANSWER:\n{golden_answer}"
    )


def _parse_match(raw: str) -> bool:
    try:
        data = json.loads(strip_markdown_fence(raw))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Answer match returned invalid JSON: {e}\n\nRaw:\n{raw}"
        ) from e
    return bool(data["matches"])


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def check_match(
    question: str, generated_answer: str, golden_answer: str
) -> bool:
    client = _get_client()
    response = await client.chat.completions.create(
        model=MATCH_MODEL,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_message(
                    question, generated_answer, golden_answer
                ),
            },
        ],
    )
    raw = response.choices[0].message.content or "{}"
    return _parse_match(raw)
