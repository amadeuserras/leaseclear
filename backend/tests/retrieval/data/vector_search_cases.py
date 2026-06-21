from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class VectorSearchCase:
    question: str
    expected_clause: str


CASES = [
    VectorSearchCase("What is the monthly rent?", "3. Rent"),
    VectorSearchCase("How much is the security deposit?", "5. Security Deposit"),
    VectorSearchCase("When does the lease end?", "2. Term"),
    VectorSearchCase("Can the tenant have pets?", "7. Pets"),
    VectorSearchCase(
        "How much notice must the landlord give before entering?",
        "9. Entry",
    ),
    VectorSearchCase("What is the pet deposit?", "2. Pet Deposit and Rent"),
]


def as_pytest_params() -> list:
    return [pytest.param(case.question, case.expected_clause) for case in CASES]
