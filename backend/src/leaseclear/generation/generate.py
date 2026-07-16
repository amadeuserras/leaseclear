from __future__ import annotations

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from leaseclear.core.config import settings
from leaseclear.types import ChunkBase, DocumentMetadata, GenerationStreamMeta

REFUSAL_MESSAGE = "This is not specified in the provided lease clauses."

SYSTEM_PROMPT = f"""
Answer questions using only the provided lease clauses.

Rules:
- Do not use outside knowledge or make assumptions.
- Every factual sentence must end with the citation ID of its supporting clause
(e.g. [doc §3]). Repeat the ID on every sentence that uses that clause — do not
rely on an earlier citation to cover later sentences.
- Quotes, checkbox states, arithmetic, and conclusions drawn from cited figures
are factual claims and need a citation on the same sentence.
- Lead with the direct answer, then stop. Add at most one extra cited sentence
when it changes the meaning (e.g. a statutory cap, a condition, an unchecked
box). Do not restate the clause, add unrelated facts, or narrate.
- Copy citation IDs exactly as provided — never invent or alter them.
- If the answer is not supported by the lease clauses, the first sentence must
be exactly:
"{REFUSAL_MESSAGE}"
  You may then add one short cited sentence explaining what is missing.
"""


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
        model="claude-sonnet-4-6",
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
