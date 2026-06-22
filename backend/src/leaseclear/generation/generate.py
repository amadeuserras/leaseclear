from __future__ import annotations

import json

import anthropic

from leaseclear.core.config import settings
from leaseclear.generation.prompts import SYSTEM_PROMPT
from leaseclear.types import Citation, GenerationResult, LabelledChunk


def _build_user_message(question: str, chunks: list[LabelledChunk]) -> str:
    chunk_block = "\n\n".join(f"{c.citation_id}\n{c.text}" for c in chunks)
    return f"LEASE CLAUSES:\n\n{chunk_block}\n\nQUESTION: {question}"


def _strip_markdown_fence(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned.startswith("```"):
        return cleaned
    cleaned = cleaned.split("\n", 1)[1]
    cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()


def _parse_response(raw: str) -> GenerationResult:
    try:
        data = json.loads(_strip_markdown_fence(raw))
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude returned invalid JSON: {e}\n\nRaw:\n{raw}") from e

    return GenerationResult(
        answer=data["answer"],
        citations=[Citation(**c) for c in data.get("citations", [])],
        confidence=float(data["confidence"]),
        refusal=bool(data["refusal"]),
    )


def generate(question: str, chunks: list[LabelledChunk]) -> GenerationResult:
    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_message(question, chunks)}],
    )
    block = response.content[0]
    if block.type != "text":
        raise ValueError(f"Expected text block, got {block.type}")
    return _parse_response(block.text)
