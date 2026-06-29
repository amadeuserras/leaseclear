from __future__ import annotations

from leaseclear.db.connection import DbConnection
from leaseclear.ingestion.embed import embed_texts
from leaseclear.types import ChunkBase

DEFAULT_SIMILARITY_FLOOR = 0.35


async def search(
    conn: DbConnection,
    question: str,
    top_k: int = 20,
    similarity_floor: float | None = DEFAULT_SIMILARITY_FLOOR,
) -> list[ChunkBase]:
    [query_vector] = embed_texts([question])
    rows = await conn.fetch(
        """--sql
        SELECT chunk_id, document_id, document_slug, text, clause_label,
               page_number, char_start, char_end, token_count
        FROM chunks
        WHERE ($3::float IS NULL OR 1 - (embedding <=> $1) >= $3)
        ORDER BY embedding <=> $1
        LIMIT $2
        """,
        str(query_vector),
        top_k,
        similarity_floor,
    )
    return [ChunkBase(**dict(row)) for row in rows]
