from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from leaseclear.api.query import run_query
from leaseclear.api.schemas import HealthResponse, QueryRequest, QueryResponse
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


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest) -> QueryResponse:
    return await run_query(request.question, request.document_ids)
