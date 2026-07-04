from __future__ import annotations

import asyncpg

from leaseclear.db.connection import apply_schema, db_session, use_database


async def ensure_database(database_url: str) -> None:
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


async def create_database(database_url: str) -> None:
    await ensure_database(database_url)
    async with use_database(database_url), db_session():
        await apply_schema()
