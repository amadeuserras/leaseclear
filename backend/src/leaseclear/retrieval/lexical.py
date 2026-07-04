from __future__ import annotations

import re
from uuid import UUID

from leaseclear.db.connection import get_conn
from leaseclear.types import ChunkBase


def _or_query(question: str) -> str:
    """Question text -> websearch query matching ANY of its words.

    plainto_tsquery ANDs every term, so one term absent from a chunk (e.g.
    "dog" in a question about a cats-only lease) discards it entirely, and
    punctuation like "Lindqvist/Patel" survives as a single lexeme that no
    chunk contains. Splitting on non-word characters and OR-ing the words
    fixes both; ts_rank still ranks multi-term matches first.
    """
    return " OR ".join(re.findall(r"\w+", question))


async def search(
    question: str,
    top_k: int = 20,
    document_ids: list[UUID] | None = None,
) -> list[ChunkBase]:
    rows = await get_conn().fetch(
        """--sql
        SELECT id, document_id, document_slug, text, clause_number, clause_label,
               page_number, char_start, char_end, token_count
        FROM chunks
        WHERE text_tsv @@ websearch_to_tsquery('english', $1)
          AND ($3::uuid[] IS NULL OR document_id = ANY($3))
        ORDER BY ts_rank(text_tsv, websearch_to_tsquery('english', $1)) DESC
        LIMIT $2
        """,
        _or_query(question),
        top_k,
        document_ids,
    )
    return [ChunkBase(**dict(row)) for row in rows]
