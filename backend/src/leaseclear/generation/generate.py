from __future__ import annotations

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from leaseclear.core.config import settings
from leaseclear.generation.prompts import SYSTEM_PROMPT
from leaseclear.types import LabelledChunk


def _build_user_message(question: str, chunks: list[LabelledChunk]) -> str:
    chunk_block = "\n\n".join(f"{c.citation_id}\n{c.text}" for c in chunks)
    return f"LEASE CLAUSES:\n\n{chunk_block}\n\nQUESTION: {question}"


async def generate_stream(
    question: str,
    chunks: list[LabelledChunk],
) -> AsyncIterator[str]:
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_user_message(question, chunks)}],
    ) as stream:
        async for token in stream.text_stream:
            yield token
