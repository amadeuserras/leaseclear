from __future__ import annotations

import asyncpg

from leaseclear.db.connection import DbConnection, apply_schema
from leaseclear.ingestion.store import store_chunks
from tests.corpus_fixture import load_seed_corpus


async def ensure_database_exists(database_url: str) -> None:
    db_name = database_url.rsplit("/", 1)[-1]
    admin_url = f"{database_url.rsplit('/', 1)[0]}/postgres"
    conn = await asyncpg.connect(admin_url)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1",
            db_name,
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
    finally:
        await conn.close()


async def truncate_db(conn: DbConnection) -> None:
    await conn.execute("TRUNCATE chunks, logs, users")


async def reset_and_seed_lease(conn: DbConnection) -> int:
    await apply_schema(conn)
    await truncate_db(conn)
    embedded = load_seed_corpus()
    await store_chunks(conn, embedded)
    return len(embedded)
