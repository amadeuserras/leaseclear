from __future__ import annotations

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from leaseclear.core.config import settings
from leaseclear.generation.prompts import SYSTEM_PROMPT
from leaseclear.types import ChunkBase, GenerationStreamMeta


def build_user_message(question: str, chunks: list[ChunkBase]) -> str:
    chunk_block = "\n\n".join(f"{c.citation_id}\n{c.text}" for c in chunks)
    return f"LEASE CLAUSES:\n\n{chunk_block}\n\nQUESTION: {question}"


async def _token_stream(
    question: str,
    chunks: list[ChunkBase],
    meta: GenerationStreamMeta,
) -> AsyncIterator[str]:
    client = AsyncAnthropic(api_key=settings.anthropic_generate_api_key)
    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(question, chunks)}],
    ) as stream:
        async for token in stream.text_stream:
            yield token
        message = await stream.get_final_message()
        meta.input_tokens = message.usage.input_tokens
        meta.output_tokens = message.usage.output_tokens


def generate_stream(
    question: str,
    chunks: list[ChunkBase],
) -> tuple[AsyncIterator[str], GenerationStreamMeta]:
    meta = GenerationStreamMeta()
    return _token_stream(question, chunks, meta), meta
