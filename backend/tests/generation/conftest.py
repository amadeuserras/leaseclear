from __future__ import annotations

from uuid import uuid4

import pytest

from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.types import Citation, GenerationResult, LabelledChunk


@pytest.fixture
def chunks() -> list[LabelledChunk]:
    return [
        LabelledChunk(
            citation_id="[lease §3. Rent]",
            chunk_id=str(uuid4()),
            text="Tenant shall pay Rent of $2,875.00 per month.",
        ),
        LabelledChunk(
            citation_id="[lease §4. Security Deposit]",
            chunk_id=str(uuid4()),
            text="Tenant shall deposit $5,750.00 as a security deposit.",
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
