"""Export parse + chunk JSON for a PDF without metadata or embedding API calls."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from leaseclear.ingestion.assign import assign_document
from leaseclear.ingestion.chunk import chunk_documents
from leaseclear.ingestion.parse import parse_document
from leaseclear.types import ChunkBase, UploadDocument

REPO_ROOT = Path(__file__).resolve().parents[2]
PDF = REPO_ROOT / "corpus" / "generated" / "texas-washington_price.pdf"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "tests" / "data"


def _source_pdf_ref(pdf: Path) -> str:
    resolved = pdf.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def _chunk_to_dict(chunk: ChunkBase) -> dict:
    return {
        **asdict(chunk),
        "id": str(chunk.id),
        "document_id": str(chunk.document_id),
        "citation_id": chunk.citation_id,
    }


def main() -> None:
    if not PDF.is_file():
        raise FileNotFoundError(f"PDF not found: {PDF}")

    upload = UploadDocument(path=str(PDF.resolve()), filename=PDF.name)
    parsed = parse_document(upload)
    assigned = assign_document(parsed, set())
    chunks = chunk_documents([assigned])

    source_pdf = _source_pdf_ref(PDF)
    stem = PDF.stem
    parsed_path = OUTPUT_DIR / f"{stem}_parsed.json"
    chunks_path = OUTPUT_DIR / f"{stem}_chunks.json"

    parsed_payload = {
        "source_pdf": source_pdf,
        **asdict(parsed),
    }
    chunks_payload = {
        "source_pdf": source_pdf,
        "document": {
            "id": str(assigned.id),
            "slug": assigned.slug,
            "filename": assigned.filename,
        },
        "chunks": [_chunk_to_dict(chunk) for chunk in chunks],
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    parsed_path.write_text(
        json.dumps(parsed_payload, indent=2, ensure_ascii=False) + "\n"
    )
    chunks_path.write_text(
        json.dumps(chunks_payload, indent=2, ensure_ascii=False) + "\n"
    )
    print(f"Wrote parsed output to {parsed_path}")
    print(f"Wrote chunk output to {chunks_path}")


if __name__ == "__main__":
    main()
