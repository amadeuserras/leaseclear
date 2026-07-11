from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_BACKEND_ROOT / ".env")
    cors_origins: list[str]
    demo_email: str = "demo@leaseclear.example"
    database_url: str
    test_database_url: str
    eval_database_url: str
    openai_api_key: str
    anthropic_api_key: str
    jwt_secret: str
    google_client_id: str | None = None


settings = Settings()  # pyright: ignore[reportCallIssue]
