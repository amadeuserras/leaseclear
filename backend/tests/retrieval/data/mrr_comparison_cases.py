from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MrrCase:
    query: str
    expected_clause_number: str | None


CASES = [
    MrrCase("Show me the security deposit section", "5"),
    MrrCase("quiet enjoyment", "8"),
    MrrCase("early termination", "14"),
    MrrCase("$40", "3"),
    MrrCase("MRL-204", None),
    MrrCase("$100,000", "12"),
]
