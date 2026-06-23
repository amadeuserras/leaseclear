from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class QueryRequest(BaseModel):
    question: str
    document_ids: list[str] | None = None


class Citation(BaseModel):
    chunk_id: str
    clause_label: str
    page_number: int
    passage: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: float
