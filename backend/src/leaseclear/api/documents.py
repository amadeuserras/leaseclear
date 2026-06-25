from __future__ import annotations

import os
import shutil
import tempfile
import uuid

from fastapi import HTTPException, UploadFile

from leaseclear.api.schemas import DocumentResponse
from leaseclear.db.connection import get_pool
from leaseclear.ingestion.chunk import chunk_document
from leaseclear.ingestion.embed import embed_chunks
from leaseclear.ingestion.parse import parse_pdf
from leaseclear.ingestion.store import store_chunks, store_document


async def ingest_document(pdf_path: str, document_id: str, filename: str) -> int:
    parsed = parse_pdf(pdf_path)
    chunks = chunk_document(parsed, document_id)
    embedded = embed_chunks(chunks)

    pool = await get_pool()
    async with pool.acquire() as conn, conn.transaction():
        await store_document(conn, document_id, filename)
        await store_chunks(conn, embedded)

    return len(chunks)


async def upload_document(file: UploadFile) -> DocumentResponse:
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    document_id = str(uuid.uuid4())

    filename = file.filename or ""

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        chunks_created = await ingest_document(tmp_path, document_id, filename)
    finally:
        os.unlink(tmp_path)

    return DocumentResponse(
        document_id=document_id,
        filename=filename,
        chunks_created=chunks_created,
    )
