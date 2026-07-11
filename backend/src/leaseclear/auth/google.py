from __future__ import annotations

import httpx
from fastapi import HTTPException

from leaseclear.core.config import settings

GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def require_google_configured() -> None:
    if not settings.google_client_id:
        raise HTTPException(status_code=503, detail="Google sign-in is not configured")


async def email_from_access_token(access_token: str) -> str:
    async with httpx.AsyncClient(timeout=15.0) as client:
        res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )
    if res.status_code != 200:
        raise HTTPException(status_code=401, detail="Google userinfo failed")
    profile = res.json()
    email = profile.get("email")
    if not email or not profile.get("email_verified"):
        raise HTTPException(status_code=401, detail="Google email not verified")
    return str(email).lower()
