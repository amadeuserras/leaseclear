from __future__ import annotations

from passlib.context import CryptContext

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(raw: str) -> str:
    return pwd.hash(raw)


def verify_password(raw: str, stored_hash: str) -> bool:
    return pwd.verify(raw, stored_hash)
