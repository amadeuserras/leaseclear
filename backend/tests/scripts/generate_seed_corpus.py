from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks, embed_texts
from leaseclear.ingestion.parse import parse_pdf

REPO_ROOT = Path(__file__).resolve().parents[3]
OUT = REPO_ROOT / "backend" / "tests" / "fixtures" / "seed_corpus.json"

SOURCES: list[tuple[Path, str]] = [
    (
        REPO_ROOT / "backend" / "tests" / "fixtures" / "test_lease.pdf",
        "test_lease",
    ),
]

# Queries used by default (non-real_api) tests that call embed_texts at search time.
TEST_QUERIES = [
    "How much is the security deposit?",
]


def main() -> None:
    all_embedded = []
    for pdf_path, document_id in SOURCES:
        document = parse_pdf(pdf_path)
        chunks = chunk_document(document, document_id)
        all_embedded.extend(embed_chunks(chunks))

    query_embeddings = {
        query: embedding
        for query, embedding in zip(
            TEST_QUERIES, embed_texts(TEST_QUERIES), strict=True
        )
    }

    payload = {
        "chunks": [asdict(chunk) for chunk in all_embedded],
        "query_embeddings": query_embeddings,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload))
    print(f"Wrote {len(all_embedded)} chunks to {OUT}")


if __name__ == "__main__":
    main()
