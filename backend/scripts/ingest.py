import argparse
import asyncio
from pathlib import Path
from uuid import UUID

from leaseclear.auth.users import register_user
from leaseclear.db.connection import apply_schema, close_pool, db_session
from leaseclear.ingestion.ingest import ingest_documents
from leaseclear.types import UploadDocument

GENERATED_DIR = Path(__file__).resolve().parents[2] / "corpus" / "generated"


def discover_pdfs() -> list[Path]:
    return sorted(GENERATED_DIR.glob("*.pdf"))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--owner-email",
        help=(
            "register this user (the schema reset wipes existing ones) and "
            "assign the ingested documents to them, so they are queryable "
            "through the authenticated API"
        ),
    )
    parser.add_argument(
        "--owner-password",
        help="password for --owner-email; required together",
    )
    args = parser.parse_args()
    if (args.owner_email is None) != (args.owner_password is None):
        parser.error("--owner-email and --owner-password must be used together")
    return args


async def main() -> None:
    args = _parse_args()
    pdfs = discover_pdfs()
    if not pdfs:
        raise SystemExit(
            f"No PDFs found in {GENERATED_DIR}. "
            "Run `uv run python generate.py` from corpus/ first."
        )

    uploads = [UploadDocument(path=str(pdf), filename=pdf.name) for pdf in pdfs]

    try:
        async with db_session() as conn:
            await apply_schema()
            await conn.execute("TRUNCATE logs, chunks, documents")

            user_id: UUID | None = None
            if args.owner_email:
                user_id = UUID(
                    await register_user(args.owner_email, args.owner_password)
                )
                print(f"Registered owner {args.owner_email} ({user_id})")

            chunks = await ingest_documents(uploads, user_id=user_id)
            print(
                f"Ingested {len(chunks)} chunks from {len(pdfs)} PDFs "
                f"in {GENERATED_DIR}"
            )
            for pdf in pdfs:
                print(f"  - {pdf.name}")
    finally:
        await close_pool()


if __name__ == "__main__":
    asyncio.run(main())
