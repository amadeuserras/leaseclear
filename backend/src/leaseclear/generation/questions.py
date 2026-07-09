from __future__ import annotations

import json
import re

from anthropic import AsyncAnthropic
from anthropic.types import TextBlock

from leaseclear.core.config import settings
from leaseclear.types import ChunkBase, DocumentMetadata

MODEL = "claude-haiku-4-5"
MAX_CHUNKS = 40
CHUNK_CHAR_CAP = 500

SYSTEM_PROMPT = (
    "You write suggested starter questions for a lease-Q&A app. Every question "
    "you write is about ONE specific tenant's lease. The app mixes these in with "
    "questions about OTHER tenants' leases, so each one must make clear WHICH "
    "lease it is about by naming ONE real detail of this document — a tenant name "
    "(full or just a surname), the landlord, the property address (full or "
    "partial), or part of the file name. Use only ONE identifier per question and "
    "ask about ONE topic; never stack multiple names, addresses, or topics into a "
    "single question. "
    "Write the way real people actually type. About half the questions should be "
    "short and lazy — roughly 3 to 7 words, one identifier, e.g. \"how much is "
    "Chen's deposit?\" or \"pets ok at Larkspur?\" — and the rest can be normal, "
    "well-formed questions. Every question must be answerable from the clauses "
    "provided, stay under 14 words, and together cover varied topics. "
    "Reply with ONLY a JSON array of question strings — no prose, no keys."
)


def _describe_document(doc: DocumentMetadata) -> str:
    tenants = ", ".join(doc.tenant_names) or "unknown"
    landlord = doc.landlord_name or "unknown"
    address = doc.property_address or "unknown"
    return (
        f"tenant(s): {tenants}; landlord: {landlord}; "
        f"property: {address}; file: {doc.filename}"
    )


def _build_prompt(
    chunks: list[ChunkBase], document: DocumentMetadata, count: int
) -> str:
    clause_block = "\n\n".join(
        f"{c.clause_label or 'clause'}: {c.text[:CHUNK_CHAR_CAP]}"
        for c in chunks[:MAX_CHUNKS]
    )
    return (
        f"DOCUMENT (every question must name one real detail of it — tenant, "
        f"landlord, address, or file name):\n{_describe_document(document)}"
        f"\n\nCLAUSES:\n{clause_block}\n\n"
        f"Write {count} suggested questions about this lease as a JSON array of "
        f"strings. Vary the topics."
    )


def _parse_questions(text: str, count: int) -> list[str]:
    text = text.strip()
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                questions = [str(q).strip() for q in parsed if str(q).strip()]
                return questions[:count]
        except json.JSONDecodeError:
            pass
    # Fallback: one question per non-empty line, stripped of list markers.
    lines = [
        re.sub(r"^[\s\-\*\d\.\"]+", "", ln).strip(' "') for ln in text.splitlines()
    ]
    return [ln for ln in lines if ln][:count]


async def generate_questions(
    chunks: list[ChunkBase],
    document: DocumentMetadata,
    count: int,
) -> list[str]:
    if not chunks:
        return []
    client = AsyncAnthropic(api_key=settings.anthropic_generate_api_key)
    message = await client.messages.create(
        model=MODEL,
        max_tokens=800,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _build_prompt(chunks, document, count)}],
    )
    text = "".join(
        block.text for block in message.content if isinstance(block, TextBlock)
    )
    return _parse_questions(text, count)
