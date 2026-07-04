from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from leaseclear.auth.jwt import decode_token

security = HTTPBearer()


async def current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> UUID:
    sub = decode_token(creds.credentials)
    try:
        return UUID(sub)
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid or expired token"
        ) from None
