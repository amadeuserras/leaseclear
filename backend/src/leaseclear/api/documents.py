from __future__ import annotations

import os
import shutil
import tempfile
from uuid import UUID

from fastapi import HTTPException, UploadFile

from leaseclear.api.schemas import DocumentChunkResponse, DocumentResponse
from leaseclear.db.connection import db_session
from leaseclear.ingestion.documents import delete_document as delete_db_document
from leaseclear.ingestion.documents import get_document_chunks as get_db_document_chunks
from leaseclear.ingestion.documents import get_documents as get_db_documents
from leaseclear.ingestion.ingest import ingest_documents
from leaseclear.types import UploadDocument


async def upload_documents(files: list[UploadFile], user_id: UUID) -> None:
    if not files:
        raise HTTPException(status_code=400, detail="At least one PDF file is required")

    for file in files:
        if file.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    pending: list[UploadDocument] = []
    temp_paths: list[str] = []

    try:
        for file in files:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                shutil.copyfileobj(file.file, tmp)
                temp_paths.append(tmp.name)

            pending.append(
                UploadDocument(path=temp_paths[-1], filename=file.filename or "")
            )

        await ingest_documents(pending, user_id=user_id)
    finally:
        for path in temp_paths:
            os.unlink(path)


async def get_documents(user_id: UUID) -> list[DocumentResponse]:
    async with db_session():
        docs = await get_db_documents(user_id)
    return [
        DocumentResponse(
            id=d.id,
            filename=d.filename,
            slug=d.slug,
            landlord_name=d.landlord_name,
            tenant_names=d.tenant_names,
            property_address=d.property_address,
        )
        for d in docs
    ]


async def get_document_chunks(slug: str, user_id: UUID) -> list[DocumentChunkResponse]:
    async with db_session():
        chunks = await get_db_document_chunks(slug, user_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="Document not found")
    return [
        DocumentChunkResponse(
            chunk_id=c.id,
            clause_number=c.clause_number,
            clause_title=c.clause_title,
            start_page=c.start_page,
            end_page=c.end_page,
            index=c.index,
            citation_id=c.citation_id,
            text=c.text,
        )
        for c in chunks
    ]


async def delete_document(document_id: UUID, user_id: UUID) -> None:
    async with db_session():
        deleted = await delete_db_document(document_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
