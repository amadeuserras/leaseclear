from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID

from leaseclear.types import EmbeddedChunk

_DATA_DIR = Path(__file__).resolve().parent

CORPUS_LEASE_PDF = _DATA_DIR / "test_lease.pdf"
CORPUS_LEASE_DOCUMENT_ID = UUID("00000000-0000-4000-8000-000000000001")
TEST_LEASE_CHUNKS_PATH = _DATA_DIR / "test_lease_chunks.json"

_fixture_data = json.loads(TEST_LEASE_CHUNKS_PATH.read_text())
SEED_CHUNKS = [
    EmbeddedChunk(
        id=UUID(chunk["id"]),
        document_id=UUID(chunk["document_id"]),
        document_slug=chunk["document_slug"],
        text=chunk["text"],
        clause_label=chunk["clause_label"],
        page_number=chunk["page_number"],
        char_start=chunk["char_start"],
        char_end=chunk["char_end"],
        token_count=chunk["token_count"],
        embedding=chunk["embedding"],
    )
    for chunk in _fixture_data["chunks"]
]
