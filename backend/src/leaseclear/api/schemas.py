from uuid import UUID

from pydantic import BaseModel, EmailStr


class HealthResponse(BaseModel):
    status: str


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class QueryRequest(BaseModel):
    question: str
    document_ids: list[UUID] | None = None


class SuggestedQuestionsRequest(BaseModel):
    document_ids: list[UUID] | None = None


class Citation(BaseModel):
    chunk_id: UUID
    clause_label: str
    page_number: int
    passage: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]


class DocumentChunkResponse(BaseModel):
    chunk_id: UUID
    clause_number: str | None
    clause_label: str | None
    page_number: int
    char_start: int
    passage: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    slug: str
    landlord_name: str | None
    tenant_names: list[str]
    property_address: str | None


class SuggestedQuestionsResponse(BaseModel):
    questions: list[str]
