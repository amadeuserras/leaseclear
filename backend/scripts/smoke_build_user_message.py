# ruff: noqa: E501

from __future__ import annotations

from uuid import UUID

from leaseclear.generation.generate import _build_user_message
from leaseclear.types import ChunkBase

question = "How much is the security deposit?"

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

example_output = """\
LEASE CLAUSES:

[lease §3. Rent]
3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.

[lease §4. Security Deposit]
4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.

QUESTION: How much is the security deposit?"""


def run() -> None:
    print(_build_user_message(question, chunks))


if __name__ == "__main__":
    run()
