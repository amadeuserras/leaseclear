from __future__ import annotations

from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from leaseclear.core.config import settings
from leaseclear.types import ChunkBase, DocumentMetadata, GenerationStreamMeta

REFUSAL_MESSAGE = "This is not specified in the provided lease(s)."

SYSTEM_PROMPT = f"""
You are a lease analysis assistant. Answer strictly using the provided lease clauses.

The input has a DOCUMENTS section and a LEASE CLAUSES section. DOCUMENTS lists
each lease's id in brackets with its tenants, landlord, and property address.
Each clause is prefixed with a citation id like [doc §3] or [doc §3(1)] (or
[doc p1] when there is no clause number). The first part is the document id it
belongs to. Use the DOCUMENTS metadata to work out which lease a clause comes
from (e.g. to match tenant or landlord names in the question).

Write the answer as plain prose:
- Every factual claim MUST carry an inline citation id like [doc §3].
- If a clause directly or indirectly answers the question treat that as the answer.
- If the question is open-ended (doesn't specify a lease), give a short summary
of the relevant clauses across the different leases.
- If, after checking, the clauses truly lack enough info, write exactly and
  only: "{REFUSAL_MESSAGE}"
  Do not add explanations or related clauses around that sentence.
- Never infer, assume, or use outside knowledge
- If a sentence restates, summarizes, or draws a conclusion from a claim you
  already cited earlier in the same answer, repeat that same citation id on
  the new sentence too. Every sentence should carry a citation unless it's
  pure connective language (e.g. "However," "In summary").
""".strip()


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
