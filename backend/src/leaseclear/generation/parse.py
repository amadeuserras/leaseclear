from __future__ import annotations

import json

from leaseclear.generation.prompts import DELIMITER
from leaseclear.types import ChunkBase, ParsedResponse
from leaseclear.utils.text import strip_markdown_fence


def parse_response(raw: str) -> ParsedResponse:
    parts = raw.split(DELIMITER, 1)
    if len(parts) != 2:
        raise ValueError(
            f"Expected prose and metadata separated by {DELIMITER!r}\n\nRaw:\n{raw}"
        )
    prose = parts[0].rstrip()
    try:
        data = json.loads(strip_markdown_fence(parts[1]))
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Claude returned invalid metadata JSON: {e}\n\nRaw:\n{raw}"
        ) from e
    if not isinstance(data, list):
        raise ValueError(
            f"Expected metadata to be a JSON array of citation ids\n\nRaw:\n{raw}"
        )
    return ParsedResponse(prose=prose, citation_ids=data)


def resolve_citations(
    citation_ids: list[str], chunks: list[ChunkBase]
) -> list[ChunkBase]:
    by_citation = {chunk.citation_id: chunk for chunk in chunks}
    return [by_citation[cid] for cid in citation_ids if cid in by_citation]
