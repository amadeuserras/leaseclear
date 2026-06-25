from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_pdf

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "backend" / "data"

SOURCES: list[tuple[Path, str]] = [
    (REPO_ROOT / "corpus" / "generated" / "lease.pdf", "lease"),
]


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for pdf_path, document_id in SOURCES:
        document = parse_pdf(pdf_path)
        chunks = chunk_document(document, document_id)
        embedded = embed_chunks(chunks)
        out = DATA_DIR / f"{document_id}-chunks.json"
        out.write_text(json.dumps([asdict(chunk) for chunk in embedded]))
        print(f"Wrote {len(embedded)} chunks to {out}")


if __name__ == "__main__":
    main()
