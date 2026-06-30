from __future__ import annotations

from uuid import uuid4

import pytest

from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.types import ChunkBase, Citation, GenerationResult


@pytest.fixture
def chunks() -> list[ChunkBase]:
    document_id = uuid4()
    return [
        ChunkBase(
            id=uuid4(),
            document_id=document_id,
            document_slug="lease",
            text="Tenant shall pay Rent of $2,875.00 per month.",
            clause_label="3. Rent",
            page_number=1,
            char_start=0,
            char_end=50,
            token_count=10,
        ),
        ChunkBase(
            id=uuid4(),
            document_id=document_id,
            document_slug="lease",
            text="Tenant shall deposit $5,750.00 as a security deposit.",
            clause_label="4. Security Deposit",
            page_number=1,
            char_start=51,
            char_end=100,
            token_count=12,
        ),
    ]


@pytest.fixture
def cited_result() -> GenerationResult:
    return GenerationResult(
        answer="The security deposit is $5,750.00. [lease §4. Security Deposit]",
        citations=[Citation(id="[lease §4. Security Deposit]", quote="$5,750.00")],
        confidence=1.0,
    )


@pytest.fixture
def refusal_result() -> GenerationResult:
    return GenerationResult(
        answer=REFUSAL_MESSAGE,
        citations=[],
        confidence=0.0,
    )
