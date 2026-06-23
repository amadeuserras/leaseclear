from __future__ import annotations

from fastapi import FastAPI

from leaseclear.api.schemas import HealthResponse

app = FastAPI(title="LeaseClear")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")
