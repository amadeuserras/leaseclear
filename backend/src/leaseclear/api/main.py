from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, UploadFile
from sse_starlette.sse import EventSourceResponse

from leaseclear.api.documents import upload_document
from leaseclear.api.query import query_events
from leaseclear.api.schemas import DocumentResponse, HealthResponse, QueryRequest
from leaseclear.db.connection import close_pool, get_pool


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(title="LeaseClear", lifespan=lifespan)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/documents", response_model=DocumentResponse)
async def documents_upload(
    file: Annotated[UploadFile, File()],
) -> DocumentResponse:
    return await upload_document(file)


@app.post("/query")
async def query(request: QueryRequest) -> EventSourceResponse:
    return EventSourceResponse(
        query_events(request.question, request.document_ids),
    )
