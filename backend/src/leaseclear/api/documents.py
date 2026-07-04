from __future__ import annotations

import os
import shutil
import tempfile
from uuid import UUID

from fastapi import HTTPException, UploadFile

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
