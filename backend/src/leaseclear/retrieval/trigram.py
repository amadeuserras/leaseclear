from __future__ import annotations

from uuid import UUID

from leaseclear.db.connection import get_conn
from leaseclear.types import ChunkBase

DEFAULT_SIMILARITY_FLOOR = 0.1


async def search(
    question: str,
    top_k: int = 20,
    similarity_floor: float | None = DEFAULT_SIMILARITY_FLOOR,
    document_ids: list[UUID] | None = None,
) -> list[ChunkBase]:
    """Fuzzy lexical search via pg_trgm word similarity.

    Catches what stemming-based FTS misses: proper names, typos, and the
    messy OCR text of real-world PDFs. `text <->> $1` is the word-similarity
    distance (1 - word_similarity($1, text)), KNN-ordered via the GiST
    trigram index.
    """
    rows = await get_conn().fetch(
        """--sql
        SELECT id, document_id, document_slug, text, clause_number, clause_title,
               start_page, end_page, "index", citation
        FROM chunks
        WHERE ($3::float IS NULL OR word_similarity($1, text) >= $3)
          AND ($4::uuid[] IS NULL OR document_id = ANY($4))
        ORDER BY text <->> $1
        LIMIT $2
        """,
        question,
        top_k,
        similarity_floor,
        document_ids,
    )
    return [ChunkBase(**dict(row)) for row in rows]
