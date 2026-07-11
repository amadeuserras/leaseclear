from __future__ import annotations

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from leaseclear.core.config import settings
from leaseclear.generation.prompts import SYSTEM_PROMPT
from leaseclear.types import ChunkBase, DocumentMetadata, GenerationStreamMeta


def _describe_document(doc: DocumentMetadata) -> str:
    tenants = ", ".join(doc.tenant_names) or "unknown"
    landlord = doc.landlord_name or "unknown"
    address = doc.property_address or "unknown"
    return f"[{doc.slug}] tenants: {tenants}; landlord: {landlord}; address: {address}"


def _build_user_message(
    question: str,
    chunks: list[ChunkBase],
    documents: list[DocumentMetadata],
) -> str:
    document_block = "\n".join(_describe_document(d) for d in documents)
    chunk_block = "\n\n".join(f"{c.citation_id}\n{c.text}" for c in chunks)
    return (
        f"DOCUMENTS:\n\n{document_block}\n\n"
        f"LEASE CLAUSES:\n\n{chunk_block}\n\n"
        f"QUESTION: {question}"
    )


async def _token_stream(
    question: str,
    chunks: list[ChunkBase],
    documents: list[DocumentMetadata],
    meta: GenerationStreamMeta,
) -> AsyncIterator[str]:
    client = AsyncAnthropic(api_key=settings.anthropic_api_key)
    async with client.messages.stream(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": _build_user_message(question, chunks, documents),
            }
        ],
    ) as stream:
        async for token in stream.text_stream:
            yield token
        message = await stream.get_final_message()
        meta.input_tokens = message.usage.input_tokens
        meta.output_tokens = message.usage.output_tokens


def generate_stream(
    question: str,
    chunks: list[ChunkBase],
    documents: list[DocumentMetadata],
) -> tuple[AsyncIterator[str], GenerationStreamMeta]:
    meta = GenerationStreamMeta()
    return _token_stream(question, chunks, documents, meta), meta
