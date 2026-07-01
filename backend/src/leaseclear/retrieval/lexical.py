from __future__ import annotations

from leaseclear.db.connection import get_conn
from leaseclear.types import ChunkBase


async def search(
    question: str,
    top_k: int = 20,
) -> list[ChunkBase]:
    rows = await get_conn().fetch(
        """--sql
        SELECT id, document_id, document_slug, text, clause_number, clause_label,
               page_number, char_start, char_end, token_count
        FROM chunks
        WHERE text_tsv @@ plainto_tsquery('english', $1)
        ORDER BY ts_rank(text_tsv, plainto_tsquery('english', $1)) DESC
        LIMIT $2
        """,
        question,
        top_k,
    )
    return [ChunkBase(**dict(row)) for row in rows]
