from __future__ import annotations

import uuid

from asyncpg.exceptions import UniqueViolationError
from fastapi import HTTPException

from leaseclear.auth.password import hash_password, verify_password
from leaseclear.db.connection import db_session


async def register_user(email: str, password: str) -> str:
    user_id = str(uuid.uuid4())
    async with db_session() as conn:
        try:
            await conn.execute(
                "INSERT INTO users (id, email, password_hash) VALUES ($1, $2, $3)",
                uuid.UUID(user_id),
                email,
                hash_password(password),
            )
        except UniqueViolationError:
            raise HTTPException(
                status_code=409, detail="Email already registered"
            ) from None
    return user_id


async def get_user_id_by_email(email: str) -> str | None:
    async with db_session() as conn:
        row = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
    return str(row["id"]) if row is not None else None


async def authenticate_user(email: str, password: str) -> str:
    async with db_session() as conn:
        row = await conn.fetchrow(
            "SELECT id, password_hash FROM users WHERE email = $1",
            email,
        )
    if row is None or not verify_password(password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return str(row["id"])
