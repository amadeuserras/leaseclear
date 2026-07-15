# Eval summary

_Generated 2026-07-15 14:50 UTC by `scripts/run_eval.py`._

Full reports: [generation report](backend/src/leaseclear/evals/reports/eval-generation-142613-20260715.md) · [retrieval report](backend/src/leaseclear/evals/reports/eval-retrieval-145055-20260715.md)

## Generation

_Generated 2026-07-15 14:26 UTC by `scripts/run_eval.py --mode generation` against 3 golden items (0 errored)._

| Metric | Definition | Score | Target | n | Status |
|---|---|---|---|---|---|
| Retrieval recall@8 | Golden chunk was retrieved in the top 8 chunks | 100.0% | ≥ 90% | 2 | PASS |
| Faithfulness (LLM) | Claims supported by retrieved chunks text | 100.0% | ≥ 90% | 6 | PASS |
| Citation precision (LLM) | Claims supported by cited chunks | 66.7% | ≥ 90% | 6 | FAIL |
| Refusal accuracy | Correctly refuses when question is unanswerable | 100.0% | ≥ 93% | 1 | PASS |
| Answer match (LLM) | Generated answer matches golden answer | 100.0% | ≥ 90% | 2 | PASS |
| Hallucination rate (LLM) | Claims not supported by retrieved chunks | 0.0% | ≤ 5% | 6 | PASS |

*p95 time-to-first-token* – Time until the first streamed token appears: 3.26s
*p95 total query latency* – Time until the full answer is generated: 4.81s

## Retrieval

_Generated 2026-07-15 14:50 UTC by `scripts/run_eval.py --mode retrieval` against 55 golden questions with their known ground truth clauses.

### Winners

MRR: **vector+lexical+trigram** (MRR 0.80)
Recall@8: **vector+trigram** (recall 0.98)

### Strategy comparison — with document filter

| Strategy | MRR | Recall@8 |
|---|---|---|
| vector+lexical+trigram | 0.80 | 0.96 |
| vector | 0.79 | 0.95 |
| vector+trigram | 0.78 | 0.98 |
| vector+lexical | 0.75 | 0.98 |
| lexical | 0.68 | 0.96 |
| trigram+lexical | 0.67 | 0.95 |
| trigram | 0.63 | 0.91 |

### Strategy comparison — without document filter

| Strategy | MRR | Recall@8 |
|---|---|---|
| vector+trigram | 0.51 | 0.80 |
| vector+lexical+trigram | 0.50 | 0.82 |
| vector+lexical | 0.50 | 0.78 |
| vector | 0.50 | 0.82 |
| lexical | 0.40 | 0.69 |
| trigram+lexical | 0.37 | 0.78 |
| trigram | 0.28 | 0.58 |
