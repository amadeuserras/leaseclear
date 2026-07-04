from __future__ import annotations

import asyncpg

from leaseclear.core.config import settings
from leaseclear.db.connection import apply_schema, close_pool, db_session


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
    prev_url = settings.database_url
    settings.database_url = database_url
    await close_pool()
    try:
        async with db_session():
            await apply_schema()
    finally:
        settings.database_url = prev_url
        await close_pool()
