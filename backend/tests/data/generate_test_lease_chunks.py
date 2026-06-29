"""Regenerate test_lease_chunks.json from test_lease.pdf (requires OpenAI API key)."""

from __future__ import annotations

import json
from dataclasses import asdict

from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_pdf
from tests.conftest import (
    CORPUS_LEASE_DOCUMENT_ID,
    CORPUS_LEASE_PDF,
    TEST_LEASE_CHUNKS_PATH,
)


def main() -> None:
    document = parse_pdf(CORPUS_LEASE_PDF)
    chunks = chunk_document(document, CORPUS_LEASE_DOCUMENT_ID)
    all_embedded = embed_chunks(chunks)

    payload = {"chunks": [asdict(chunk) for chunk in all_embedded]}
    TEST_LEASE_CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEST_LEASE_CHUNKS_PATH.write_text(json.dumps(payload))
    print(f"Wrote {len(all_embedded)} chunks to {TEST_LEASE_CHUNKS_PATH}")


if __name__ == "__main__":
    main()
