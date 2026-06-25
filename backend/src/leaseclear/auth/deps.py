from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from leaseclear.auth.jwt import decode_token

security = HTTPBearer()


async def current_user(
    creds: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    return decode_token(creds.credentials)
