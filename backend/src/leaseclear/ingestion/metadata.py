from __future__ import annotations

import asyncio
import json

from anthropic import AsyncAnthropic

from leaseclear.core.config import settings
from leaseclear.types import AssignedDocument, EnrichedDocument
from leaseclear.utils.text import strip_markdown_fence

MODEL = "claude-haiku-4-5"
MAX_CHARS = 8000

SYSTEM_PROMPT = """
You extract structured metadata from residential lease agreements.

Read the lease text and identify:
- landlord_name: the landlord's/lessor's full legal name
- tenant_names: the tenant's/lessee's full name(s), as a list of strings
- property_address: the full address of the leased premises

Respond with JSON only, no prose, no markdown fences, in this exact shape:
{"landlord_name": ..., "tenant_names": [...], "property_address": ...}

If a field cannot be determined from the text, use null
(or an empty list for tenant_names).
""".strip()


def _get_client() -> AsyncAnthropic:
    return AsyncAnthropic(api_key=settings.anthropic_api_key)


def _document_text(document: AssignedDocument) -> str:
    full_text = "\n\n".join(page.text for page in document.pages if page.text)
    return full_text[:MAX_CHARS]


def _parse_metadata(raw: str) -> tuple[str | None, list[str], str | None]:
    try:
        data = json.loads(strip_markdown_fence(raw))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude returned invalid metadata JSON: {e}\n\nRaw:\n{raw}"
        ) from e
    return (
        data.get("landlord_name"),
        data.get("tenant_names") or [],
        data.get("property_address"),
    )


async def _extract_one(
    client: AsyncAnthropic, document: AssignedDocument
) -> EnrichedDocument:
    message = await client.messages.create(
        model=MODEL,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": _document_text(document)}],
    )
    raw = "".join(block.text for block in message.content if block.type == "text")
    landlord_name, tenant_names, property_address = _parse_metadata(raw)
    return EnrichedDocument(
        id=document.id,
        slug=document.slug,
        filename=document.filename,
        pages=document.pages,
        landlord_name=landlord_name,
        tenant_names=tenant_names,
        property_address=property_address,
    )


async def extract_metadata(
    documents: list[AssignedDocument],
) -> list[EnrichedDocument]:
    if not documents:
        return []
    client = _get_client()
    return list(await asyncio.gather(*(_extract_one(client, doc) for doc in documents)))
