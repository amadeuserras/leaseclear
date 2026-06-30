from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar
from pathlib import Path

import asyncpg
from asyncpg import Connection
from asyncpg.pool import PoolConnectionProxy

from leaseclear.core.config import settings

DbConnection = Connection | PoolConnectionProxy

_pool: asyncpg.Pool | None = None
_session_ctx: ContextVar[DbConnection] = ContextVar("db_session")


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


def get_conn() -> DbConnection:
    try:
        return _session_ctx.get()
    except LookupError:
        raise RuntimeError(
            "No database connection in context. Use db_session() context manager."
        ) from None


@asynccontextmanager
async def db_session() -> AsyncIterator[DbConnection]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        token = _session_ctx.set(conn)
        try:
            yield conn
        finally:
            _session_ctx.reset(token)


async def apply_schema() -> None:
    schema_sql = Path(__file__).with_name("schema.sql").read_text()
    schema_sql = schema_sql.strip()
    if not schema_sql:
        return
    await get_conn().execute(schema_sql)
