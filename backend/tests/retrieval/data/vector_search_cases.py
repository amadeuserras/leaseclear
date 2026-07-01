from __future__ import annotations

from dataclasses import dataclass

import pytest


@dataclass(frozen=True)
class VectorSearchCase:
    question: str
    expected_clause_number: str


CASES = [
    VectorSearchCase("What is the monthly rent?", "3"),
    VectorSearchCase("How much is the security deposit?", "5"),
    VectorSearchCase("When does the lease end?", "2"),
    VectorSearchCase("Can the tenant have pets?", "7"),
    VectorSearchCase(
        "How much notice must the landlord give before entering?",
        "9",
    ),
    VectorSearchCase("What is the pet deposit?", "2"),
]


def as_pytest_params() -> list:
    return [pytest.param(case.question, case.expected_clause_number) for case in CASES]
