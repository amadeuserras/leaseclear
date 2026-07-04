from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_BACKEND_ROOT / ".env")
    database_url: str = "postgresql://leaseclear:leaseclear@localhost:5433/leaseclear"
    test_database_url: str = (
        "postgresql://leaseclear:leaseclear@localhost:5433/leaseclear_test"
    )
    eval_database_url: str = (
        "postgresql://leaseclear:leaseclear@localhost:5433/leaseclear_eval"
    )
    openai_embeddings_api_key: str
    openai_judge_api_key: str
    anthropic_generate_api_key: str
    anthropic_metadata_api_key: str
    anthropic_filter_api_key: str
    jwt_secret: str


settings = Settings()  # pyright: ignore[reportCallIssue]
