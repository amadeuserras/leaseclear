from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextvars import ContextVar, Token
from pathlib import Path

import asyncpg
from asyncpg import Connection
from asyncpg.pool import PoolConnectionProxy

from leaseclear.core.config import settings

DbConnection = Connection | PoolConnectionProxy

_pool: asyncpg.Pool | None = None
_pool_url: str | None = None
_session_ctx: ContextVar[DbConnection] = ContextVar("db_session")
_active_url: ContextVar[str | None] = ContextVar("db_active_url", default=None)


def current_database_url() -> str:
    active = _active_url.get()
    if active is not None:
        return active
    return settings.database_url


async def get_pool() -> asyncpg.Pool:
    global _pool, _pool_url
    url = current_database_url()
    if _pool is None or _pool_url != url:
        await close_pool()
        _pool = await asyncpg.create_pool(url)
        _pool_url = url
    return _pool


async def close_pool() -> None:
    global _pool, _pool_url
    if _pool is not None:
        await _pool.close()
        _pool = None
    _pool_url = None


class _DatabaseBinding:
    def __init__(self, token: Token[str | None]) -> None:
        self._token = token


async def bind_database(database_url: str) -> _DatabaseBinding:
    token = _active_url.set(database_url)
    await close_pool()
    return _DatabaseBinding(token)


async def unbind_database(binding: _DatabaseBinding) -> None:
    _active_url.reset(binding._token)
    await close_pool()


@asynccontextmanager
async def use_database(database_url: str) -> AsyncIterator[None]:
    binding = await bind_database(database_url)
    try:
        yield
    finally:
        await unbind_database(binding)


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
