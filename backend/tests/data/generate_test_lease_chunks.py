"""Regenerate test_lease_chunks.json from test_lease.pdf (requires OpenAI API key)."""

from __future__ import annotations

import json
from dataclasses import asdict, replace

from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_document
from leaseclear.types import UploadDocument
from tests.data.corpus import CORPUS_LEASE_PDF, SEED_DOCUMENT, TEST_LEASE_CHUNKS_PATH


def main() -> None:
    upload = UploadDocument(
        path=str(CORPUS_LEASE_PDF),
        filename=CORPUS_LEASE_PDF.name,
    )
    parsed = parse_document(upload)
    assigned = replace(SEED_DOCUMENT, pages=parsed.pages)
    chunks = chunk_documents([assigned])
    all_embedded = embed_chunks(chunks)

    payload = {
        "chunks": [
            {
                **asdict(chunk),
                "id": str(chunk.id),
                "document_id": str(chunk.document_id),
            }
            for chunk in all_embedded
        ]
    }
    TEST_LEASE_CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    TEST_LEASE_CHUNKS_PATH.write_text(json.dumps(payload))
    print(f"Wrote {len(all_embedded)} chunks to {TEST_LEASE_CHUNKS_PATH}")


if __name__ == "__main__":
    main()
