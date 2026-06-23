# ruff: noqa: E501

from __future__ import annotations

from leaseclear.generation.validate import validate
from leaseclear.types import Citation, GenerationResult, LabelledChunk
from leaseclear.utils.pretty_print import pretty_print

chunks = [
    {
        "citation_id": "[lease §3. Rent]",
        "chunk_id": "lease_chunk-004",
        "text": "3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.",
    },
    {
        "citation_id": "[lease §4. Security Deposit]",
        "chunk_id": "lease_chunk-005",
        "text": "4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
    },
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
    "refusal": False,
}

example_output = {
    "passed": True,
    "phantom_ids": [],
    "uncited_claims": False,
}


def run() -> None:
    labelled_chunks = [LabelledChunk(**chunk) for chunk in chunks]
    generation_result = GenerationResult(
        answer=result["answer"],
        citations=[Citation(**citation) for citation in result["citations"]],
        confidence=result["confidence"],
        refusal=result["refusal"],
    )
    output = validate(generation_result, labelled_chunks)
    pretty_print(output)


if __name__ == "__main__":
    run()
