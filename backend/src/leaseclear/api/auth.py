from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from leaseclear.api.limiter import limiter
from leaseclear.api.schemas import (
    AuthRequest,
    GoogleAuthRequest,
    GoogleAuthResponse,
    MeResponse,
    TokenResponse,
)
from leaseclear.auth.deps import current_user
from leaseclear.auth.google import email_from_access_token, require_google_configured
from leaseclear.auth.jwt import create_token
from leaseclear.auth.users import (
    authenticate_user,
    get_or_create_oauth_user,
    get_user_email_by_id,
    get_user_id_by_email,
    register_user,
)
from leaseclear.core.config import settings

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TokenResponse)
@limiter.limit("5/minute")
async def register(request: Request, req: AuthRequest) -> TokenResponse:
    user_id = await register_user(req.email, req.password)
    return TokenResponse(access_token=create_token(user_id))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, req: AuthRequest) -> TokenResponse:
    user_id = await authenticate_user(req.email, req.password)
    return TokenResponse(access_token=create_token(user_id))


@router.get("/me", response_model=MeResponse)
async def me(user_id: Annotated[UUID, Depends(current_user)]) -> MeResponse:
    email = await get_user_email_by_id(str(user_id))
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return MeResponse(email=email)


# Deliberately not rate-limited: a public demo may see many visitors behind one
# IP, and the shared demo account is read-only. Returns a token for the seeded
# demo user (see DEMO_EMAIL); 503 if the demo data hasn't been seeded.
@router.post("/demo", response_model=TokenResponse)
async def demo() -> TokenResponse:
    user_id = await get_user_id_by_email(settings.demo_email)
    if user_id is None:
        raise HTTPException(status_code=503, detail="Demo is not available")
    return TokenResponse(access_token=create_token(user_id))


@router.post("/google", response_model=GoogleAuthResponse)
@limiter.limit("5/minute")
async def google_login(request: Request, req: GoogleAuthRequest) -> GoogleAuthResponse:
    require_google_configured()
    email = await email_from_access_token(req.access_token)
    user_id = await get_or_create_oauth_user(email)
    return GoogleAuthResponse(access_token=create_token(user_id), email=email)
