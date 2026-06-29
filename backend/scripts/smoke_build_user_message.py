# ruff: noqa: E501

from __future__ import annotations

from leaseclear.generation.generate import _build_user_message
from leaseclear.types import LabelledChunk

question = "How much is the security deposit?"

chunks = [
    {
        "citation_id": "[lease §3. Rent]",
        "id": "d0000000-0000-4000-8000-000000000004",
        "text": "3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.",
    },
    {
        "citation_id": "[lease §4. Security Deposit]",
        "id": "d0000000-0000-4000-8000-000000000005",
        "text": "4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
    },
]

example_output = """\
LEASE CLAUSES:

[lease §3. Rent]
3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.

[lease §4. Security Deposit]
4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.

QUESTION: How much is the security deposit?"""


def run() -> None:
    labelled_chunks = [LabelledChunk(**chunk) for chunk in chunks]
    print(_build_user_message(question, labelled_chunks))


if __name__ == "__main__":
    run()
