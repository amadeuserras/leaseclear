from __future__ import annotations

from fastapi import APIRouter

from leaseclear.api.schemas import AuthRequest, TokenResponse
from leaseclear.auth.jwt import create_token
from leaseclear.auth.users import authenticate_user, register_user

router = APIRouter(prefix="/auth")


@router.post("/register", response_model=TokenResponse)
async def register(req: AuthRequest) -> TokenResponse:
    user_id = await register_user(req.email, req.password)
    return TokenResponse(access_token=create_token(user_id))


@router.post("/login", response_model=TokenResponse)
async def login(req: AuthRequest) -> TokenResponse:
    user_id = await authenticate_user(req.email, req.password)
    return TokenResponse(access_token=create_token(user_id))
