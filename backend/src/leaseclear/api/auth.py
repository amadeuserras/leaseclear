from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from leaseclear.api.limiter import limiter
from leaseclear.api.schemas import AuthRequest, TokenResponse
from leaseclear.auth.jwt import create_token
from leaseclear.auth.users import (
    authenticate_user,
    get_user_id_by_email,
    register_user,
)
from leaseclear.core.config import settings

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TokenResponse)
async def register(req: AuthRequest) -> TokenResponse:
    user_id = await register_user(req.email, req.password)
    return TokenResponse(access_token=create_token(user_id))


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(request: Request, req: AuthRequest) -> TokenResponse:
    user_id = await authenticate_user(req.email, req.password)
    return TokenResponse(access_token=create_token(user_id))


# Deliberately not rate-limited: a public demo may see many visitors behind one
# IP, and the shared demo account is read-only. Returns a token for the seeded
# demo user (see DEMO_EMAIL); 503 if the demo data hasn't been seeded.
@router.post("/demo", response_model=TokenResponse)
async def demo() -> TokenResponse:
    user_id = await get_user_id_by_email(settings.demo_email)
    if user_id is None:
        raise HTTPException(status_code=503, detail="Demo is not available")
    return TokenResponse(access_token=create_token(user_id))
