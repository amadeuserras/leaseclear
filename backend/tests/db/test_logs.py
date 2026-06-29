from __future__ import annotations

from uuid import uuid4

from leaseclear.db.connection import DbConnection
from leaseclear.db.logs import insert_query_log
from leaseclear.types import QueryLogEntry


async def test_insert_query_log(seed_db: DbConnection) -> None:
    entry = QueryLogEntry(
        id=uuid4(),
        question="How much is the security deposit?",
        document_ids=["test_lease"],
        chunk_ids_retrieved=["test_lease_chunk-005"],
        ttft_s=0.42,
        total_s=1.8,
        input_tokens=512,
        output_tokens=128,
        refused=False,
    )
    await insert_query_log(seed_db, entry)

    row = await seed_db.fetchrow(
        "SELECT question, refused, chunk_ids_retrieved FROM logs WHERE id = $1",
        entry.id,
    )
    assert row is not None
    assert row["question"] == entry.question
    assert row["refused"] is False
    assert row["chunk_ids_retrieved"] == ["test_lease_chunk-005"]
