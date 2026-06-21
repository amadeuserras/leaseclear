from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MrrCase:
    query: str
    expected_clause: str


CASES = [
    MrrCase("Show me the security deposit section", "5. Security Deposit"),
    MrrCase("quiet enjoyment", "8. Quiet Enjoyment; Nuisance"),
    MrrCase("early termination", "14. Early Termination"),
    MrrCase("$40", "3. Rent"),
    MrrCase("MRL-204", ""),
    MrrCase("$100,000", "12. Insurance"),
]
