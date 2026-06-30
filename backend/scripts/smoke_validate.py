# ruff: noqa: E501

from __future__ import annotations

from uuid import UUID

from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.generation.validate import validate
from leaseclear.types import ChunkBase, Citation, GenerationResult
from leaseclear.utils.pretty_print import pretty_print

DOCUMENT_ID = UUID("d0000000-0000-4000-8000-000000000003")

chunks = [
    ChunkBase(
        id=UUID("d0000000-0000-4000-8000-000000000004"),
        document_id=DOCUMENT_ID,
        document_slug="lease",
        text="3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.",
        clause_label="3. Rent",
        page_number=1,
        char_start=0,
        char_end=90,
        token_count=25,
    ),
    ChunkBase(
        id=UUID("d0000000-0000-4000-8000-000000000005"),
        document_id=DOCUMENT_ID,
        document_slug="lease",
        text="4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
        clause_label="4. Security Deposit",
        page_number=1,
        char_start=91,
        char_end=180,
        token_count=25,
    ),
]

result = {
    "answer": "The security deposit is $5,750.00, which must be deposited prior to move-in. [lease §4. Security Deposit]",
    "citations": [
        {
            "id": "[lease §4. Security Deposit]",
            "quote": "Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
        }
    ],
    "confidence": 1.0,
}

example_output = {
    "passed": True,
    "phantom_ids": [],
    "uncited_claims": False,
}


def run() -> None:
    generation_result = GenerationResult(
        answer=result["answer"],
        citations=[Citation(**citation) for citation in result["citations"]],
        confidence=result["confidence"],
    )
    output = validate(generation_result, chunks, REFUSAL_MESSAGE)
    pretty_print(output)


if __name__ == "__main__":
    run()
