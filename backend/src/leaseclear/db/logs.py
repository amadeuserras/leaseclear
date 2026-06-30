from __future__ import annotations

from leaseclear.db.connection import get_conn
from leaseclear.types import QueryLogEntry


async def insert_query_log(entry: QueryLogEntry) -> None:
    await get_conn().execute(
        """--sql
        INSERT INTO logs (
            id, question, document_ids, chunk_ids_retrieved,
            ttft_s, total_s, input_tokens, output_tokens, refused
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        entry.id,
        entry.question,
        entry.document_ids,
        entry.chunk_ids_retrieved,
        entry.ttft_s,
        entry.total_s,
        entry.input_tokens,
        entry.output_tokens,
        entry.refused,
    )
