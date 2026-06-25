# ruff: noqa: E501
from __future__ import annotations

import asyncio
import sys

from leaseclear.generation.generate import generate_stream
from leaseclear.types import LabelledChunk

chunks = [
    LabelledChunk(
        citation_id="[lease §3. Rent]",
        chunk_id="lease_chunk-004",
        text="3. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.",
    ),
    LabelledChunk(
        citation_id="[lease §4. Security Deposit]",
        chunk_id="lease_chunk-005",
        text="4. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
    ),
]


question = "How much is the security deposit?"


async def run() -> None:
    tokens, _ = generate_stream(question, chunks)
    async for token in tokens:
        sys.stdout.write(token)
        sys.stdout.flush()


if __name__ == "__main__":
    asyncio.run(run())
