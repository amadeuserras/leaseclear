from __future__ import annotations

import json
from uuid import UUID

from openai import AsyncOpenAI

from leaseclear.core.config import settings
from leaseclear.filtering.documents import list_document_metadata
from leaseclear.types import DocumentMetadata
from leaseclear.utils.text import strip_markdown_fence

MODEL = "gpt-5-mini"

SYSTEM_PROMPT = """
You match a user's question about residential leases to the specific lease
document(s) it refers to, based on tenant names, landlord name, property
address or filename.

You will receive a JSON array of documents, each shaped like:
{"idx": 1, "tenants": [...], "landlord": ..., "address": ..., "filename": "..."}

Respond with JSON only, no prose, no markdown fences, in this exact shape:
{"idx": [1, 3]}

Rules:
- Include a document's idx only if the question identifies it by tenant
  name, landlord name, address, filename, or another clearly matching detail.
- If the question does not reference any particular document (e.g. it's a
  general question), include every idx.
- If the question references a document but none of the candidates match,
  return an empty list.
""".strip()


def _get_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=settings.openai_api_key)


def _build_metadata_prompt(
    documents: list[DocumentMetadata],
) -> tuple[str, dict[int, UUID]]:
    by_idx = {idx: doc.id for idx, doc in enumerate(documents, start=1)}
    compact = [
        {
            "idx": idx,
            "tenants": doc.tenant_names,
            "landlord": doc.landlord_name,
            "address": doc.property_address,
            "filename": doc.filename,
        }
        for idx, doc in enumerate(documents, start=1)
    ]
    return json.dumps(compact), by_idx


def _parse_indices(raw: str) -> list[int]:
    try:
        data = json.loads(strip_markdown_fence(raw))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude returned invalid filter JSON: {e}\n\nRaw:\n{raw}"
        ) from e
    return [int(idx) for idx in data.get("idx", [])]


async def filter_documents(question: str) -> list[UUID]:
    """Return the ids of documents relevant to `question`, per the filter LLM."""
    documents = await list_document_metadata()
    if not documents:
        return []

    metadata_json, by_idx = _build_metadata_prompt(documents)
    client = _get_client()
    response = await client.chat.completions.create(
        model=MODEL,
        max_completion_tokens=256,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"DOCUMENTS:\n{metadata_json}\n\nQUESTION: {question}",
            },
        ],
    )
    raw = response.choices[0].message.content or ""
    indices = _parse_indices(raw)
    return [by_idx[idx] for idx in indices if idx in by_idx]
