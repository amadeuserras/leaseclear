from __future__ import annotations

from pathlib import Path
from uuid import UUID

from leaseclear.auth.users import register_user
from leaseclear.db.connection import db_session, use_database
from leaseclear.ingestion.ingest import ingest_documents
from leaseclear.types import UploadDocument

GENERATED_DIR = Path(__file__).resolve().parents[4] / "corpus" / "generated"
OWNER_EMAIL = "owner@leaseclear.example"
OWNER_PASSWORD = "leaseclear"


def discover_generated_pdfs() -> list[Path]:
    return sorted(GENERATED_DIR.glob("*.pdf"))


async def seed_database(database_url: str) -> tuple[UUID, int, int]:
    pdfs = discover_generated_pdfs()
    if not pdfs:
        raise SystemExit(
            f"No PDFs found in {GENERATED_DIR}. "
            "Run `uv run python generate.py` from corpus/ first."
        )

    uploads = [UploadDocument(path=str(p), filename=p.name) for p in pdfs]
    async with use_database(database_url):
        async with db_session() as conn:
            await conn.execute("TRUNCATE logs, chunks, users, documents")
        user_id = UUID(await register_user(OWNER_EMAIL, OWNER_PASSWORD))
        chunks = await ingest_documents(uploads, user_id=user_id)
        return user_id, len(pdfs), len(chunks)
