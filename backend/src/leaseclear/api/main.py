from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, File, Request, UploadFile
from sse_starlette.sse import EventSourceResponse

from leaseclear.api.auth import router as auth_router
from leaseclear.api.documents import get_documents, upload_documents
from leaseclear.api.limiter import (
    RateLimitExceeded,
    limiter,
    rate_limit_exceeded_handler,
)
from leaseclear.api.query import query_events
from leaseclear.api.schemas import DocumentResponse, HealthResponse, QueryRequest
from leaseclear.auth.deps import current_user
from leaseclear.db.connection import close_pool, get_pool


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await get_pool()
    yield
    await close_pool()


app = FastAPI(title="LeaseClear", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.include_router(auth_router)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/documents", response_model=list[DocumentResponse])
async def documents_list(
    user_id: Annotated[UUID, Depends(current_user)],
) -> list[DocumentResponse]:
    return await get_documents(user_id)


@app.post("/documents", status_code=204)
@limiter.limit("5/minute")
async def documents_upload(
    request: Request,
    files: Annotated[list[UploadFile], File()],
    user_id: Annotated[UUID, Depends(current_user)],
) -> None:
    await upload_documents(files, user_id)


@app.post("/query")
@limiter.limit("10/minute")
async def query(
    request: Request,
    req: QueryRequest,
    user_id: Annotated[UUID, Depends(current_user)],
) -> EventSourceResponse:
    return EventSourceResponse(
        query_events(req.question, user_id, req.document_ids),
    )
