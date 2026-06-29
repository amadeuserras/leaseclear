# ruff: noqa: E501
"""Reciprocal Rank Fusion (RRF) — merge vector + lexical ranked lists.

Hybrid retrieval runs two searches independently:
  - vector: pgvector cosine similarity (filtered by similarity floor in SQL)
  - lexical: Postgres full-text search ranked by ts_rank

RRF combines them without normalizing scores. For each ranked list, a chunk at
rank r earns 1 / (k + r) points (k = 60 by default). A chunk that appears in
BOTH lists accumulates points from both — shared hits float to the top even when
one retriever alone ranks them lower.
"""

from __future__ import annotations

from leaseclear.utils.pretty_print import pretty_print

vector_results = [
    {
        "id": "d0000000-0000-4000-8000-000000000005",
        "clause_label": "5. Security Deposit",
        "text": "5. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
    },
    {
        "id": "d0000000-0000-4000-8000-000000000004",
        "clause_label": "4. Rent",
        "text": "4. Rent. Tenant shall pay Rent of $2,875.00 per month, due on the 1st of each month.",
    },
    {
        "id": "d0000000-0000-4000-8000-000000000011",
        "clause_label": "11. Statutory Disclosures",
        "text": "11. Statutory and Condition Disclosures. The following disclosures form part of this Agreement...",
    },
]

lexical_results = [
    {
        "id": "d0000000-0000-4000-8000-000000000005",
        "clause_label": "5. Security Deposit",
        "text": "5. Security Deposit. Tenant shall deposit $5,750.00 as a security deposit prior to move-in.",
    },
    {
        "id": "d0000000-0000-4000-8000-000000000008",
        "clause_label": "8. Maintenance",
        "text": "8. Maintenance, Use, and Reporting. Tenant shall properly use, operate, and safeguard the Premises...",
    },
]

# Fused output — re-ranked by RRF score.
#
#   d0000000-0000-4000-8000-000000000005  vector rank 1 + lexical rank 1  →  1/61 + 1/61 ≈ 0.0328
#   d0000000-0000-4000-8000-000000000004  vector rank 2 only               →  1/62       ≈ 0.0161
#   d0000000-0000-4000-8000-000000000008  lexical rank 2 only              →  1/62       ≈ 0.0161
#   d0000000-0000-4000-8000-000000000011  vector rank 3 only               →  1/63       ≈ 0.0159
example_output = [
    {
        "id": "d0000000-0000-4000-8000-000000000005",
        "clause_label": "5. Security Deposit",
        "rrf_note": "rank 1 in vector + rank 1 in lexical",
    },
    {
        "id": "d0000000-0000-4000-8000-000000000004",
        "clause_label": "4. Rent",
        "rrf_note": "rank 2 in vector only",
    },
    {
        "id": "d0000000-0000-4000-8000-000000000008",
        "clause_label": "8. Maintenance",
        "rrf_note": "rank 2 in lexical only",
    },
    {
        "id": "d0000000-0000-4000-8000-000000000011",
        "clause_label": "11. Statutory Disclosures",
        "rrf_note": "rank 3 in vector only",
    },
]


def run() -> None:
    pretty_print(vector_results, "Vector input")
    pretty_print(lexical_results, "Lexical input")
    pretty_print(example_output, "Fused output (RRF rank order)")


if __name__ == "__main__":
    run()
