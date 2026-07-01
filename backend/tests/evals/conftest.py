from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from leaseclear.core.config import settings
from leaseclear.db.connection import apply_schema, close_pool, db_session, get_conn
from leaseclear.evals.golden.loader import GoldenItem, load_golden_items
from leaseclear.evals.pipeline import run_all
from leaseclear.evals.types import CaseResult

GENERATED_DIR = Path(__file__).resolve().parents[3] / "corpus" / "generated"


@pytest.fixture(scope="session")
def golden_items() -> list[GoldenItem]:
    return load_golden_items()


@pytest.fixture(scope="session")
async def full_corpus_db(
    database_url: str, ensure_test_database: None
) -> AsyncIterator[None]:
    """Ingest the full generated corpus into the test database, once per session.

    Points `settings.database_url` at the test DB (same trick tests/api/conftest.py
    uses) so the pipeline exercises the exact connection-pool path production
    code uses, instead of a special-cased test-only wiring.

    Imports ingestion lazily: it pulls in tiktoken, which fetches its BPE
    file over the network on first use. That cost belongs to this `eval`
    fixture alone, not to collecting the fast, offline tests in this
    directory.
    """
    pdfs = sorted(GENERATED_DIR.glob("*.pdf"))
    if not pdfs:
        pytest.skip(
            f"no PDFs in {GENERATED_DIR}; run `uv run python generate.py` "
            "in corpus/ first"
        )

    from leaseclear.ingestion.ingest import ingest_documents
    from leaseclear.types import UploadDocument

    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(settings, "database_url", database_url)
    await close_pool()
    try:
        async with db_session():
            await apply_schema()
            await get_conn().execute("TRUNCATE chunks, logs, users, documents")
        uploads = [UploadDocument(path=str(p), filename=p.name) for p in pdfs]
        await ingest_documents(uploads)
        yield
    finally:
        async with db_session():
            await get_conn().execute("TRUNCATE chunks, logs, users, documents")
        await close_pool()
        monkeypatch.undo()


@pytest.fixture(scope="session")
async def case_results(
    full_corpus_db: None, golden_items: list[GoldenItem]
) -> list[CaseResult]:
    """Run the whole golden set through the pipeline once per session.

    Every real_api call (embeddings, generation, judge) costs money, so this
    is shared across every `eval`-marked test that wants to assert on a
    metric, instead of each test re-running the full suite.
    """
    return await run_all(golden_items)
