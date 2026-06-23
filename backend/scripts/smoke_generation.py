# ruff: noqa: E501

from __future__ import annotations

from leaseclear.generation.generate import generate
from leaseclear.types import LabelledChunk
from leaseclear.utils.pretty_print import pretty_print

question = "How much is the security deposit?"

chunks = [
    {
        "citation_id": "[lease §3. Rent]",
        "chunk_id": "lease_chunk-004",
        "text": "3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.",
        "similarity": 0.91,
    },
    {
        "citation_id": "[lease §4. Security Deposit]",
        "chunk_id": "lease_chunk-005",
        "text": "4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
        "similarity": 0.87,
    },
]

example_output = {
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


def run() -> None:
    labelled_chunks = [LabelledChunk(**chunk) for chunk in chunks]
    result = generate(question, labelled_chunks)
    pretty_print(result)


if __name__ == "__main__":
    run()
