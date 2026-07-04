from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

import pytest

from leaseclear.core.config import settings
from leaseclear.db.connection import (
    apply_schema,
    bind_database,
    db_session,
    get_conn,
    unbind_database,
)
from leaseclear.db.create import ensure_database
from leaseclear.evals.golden.loader import GoldenItem, load_golden_items
from leaseclear.evals.pipeline import run_all
from leaseclear.evals.types import CaseResult

GENERATED_DIR = Path(__file__).resolve().parents[3] / "corpus" / "generated"


@pytest.fixture(scope="session")
def golden_items() -> list[GoldenItem]:
    return load_golden_items()


@pytest.fixture(scope="session")
def eval_database_url() -> str:
    return settings.eval_database_url


@pytest.fixture(scope="session")
async def ensure_eval_database(eval_database_url: str) -> None:
    await ensure_database(eval_database_url)


@pytest.fixture(scope="session")
async def eval_db(
    ensure_eval_database: None, eval_database_url: str
) -> AsyncIterator[None]:
    binding = await bind_database(eval_database_url)
    try:
        yield
    finally:
        await unbind_database(binding)


@pytest.fixture(scope="session")
async def full_corpus_db(eval_db: None) -> AsyncIterator[None]:
    """Ingest the full generated corpus into the eval database, once per session.

    Routes the connection pool to the eval DB via `bind_database()` so the
    pipeline exercises the same path production code uses.

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

    async with db_session():
        await apply_schema()
        await get_conn().execute("TRUNCATE chunks, logs, users, documents")
    uploads = [UploadDocument(path=str(p), filename=p.name) for p in pdfs]
    await ingest_documents(uploads)
    yield
    async with db_session():
        await get_conn().execute("TRUNCATE chunks, logs, users, documents")


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
