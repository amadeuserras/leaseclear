from __future__ import annotations

from pathlib import Path

import asyncpg
from asyncpg import Connection
from asyncpg.pool import PoolConnectionProxy

from leaseclear.core.config import settings

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(settings.database_url)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


async def apply_schema(conn: Connection | PoolConnectionProxy) -> None:
    schema_sql = Path(__file__).with_name("schema.sql").read_text()
    statements = [
        statement.strip() for statement in schema_sql.split(";") if statement.strip()
    ]
    for statement in statements:
        await conn.execute(statement)
