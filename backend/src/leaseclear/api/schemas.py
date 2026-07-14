from uuid import UUID

from pydantic import BaseModel, EmailStr


class HealthResponse(BaseModel):
    status: str


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    access_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class GoogleAuthResponse(TokenResponse):
    email: EmailStr


class MeResponse(BaseModel):
    email: EmailStr


class QueryRequest(BaseModel):
    question: str
    document_ids: list[UUID] | None = None


class SuggestedQuestionsRequest(BaseModel):
    document_ids: list[UUID] | None = None


class QueryResponse(BaseModel):
    answer: str


class DocumentChunkResponse(BaseModel):
    chunk_id: UUID
    clause_number: str | None
    clause_title: str | None
    start_page: int
    end_page: int
    index: int
    citation_id: str
    text: str


class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    slug: str
    landlord_name: str | None
    tenant_names: list[str]
    property_address: str | None


class SuggestedQuestionsResponse(BaseModel):
    questions: list[str]
