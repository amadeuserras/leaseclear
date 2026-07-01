> **Status: harness built, not yet run for real.** This file is committed by
> hand from the exact renderer the CI job uses
> (`leaseclear.evals.report.render_metrics_md`), so the shape below is
> accurate — but every score is `n/a` because generating real numbers needs
> live `OPENAI_EMBEDDINGS_API_KEY`, `OPENAI_JUDGE_API_KEY`, and
> `ANTHROPIC_GENERATE_API_KEY` credentials plus an ingested corpus, neither of
> which is available where this was written. Run `uv run python
> scripts/run_evals.py` locally (after `uv run python scripts/ingest.py`), or
> trigger the `Evals` GitHub Action, to overwrite this file with a real run.

# METRICS

_Generated 2026-07-01 16:53 UTC by `scripts/run_evals.py` against 0 golden items (0 errored)._

The golden dataset (`backend/src/leaseclear/evals/golden/golden.jsonl`) is intentionally small right now while the harness is being proven out. CP7's target shape is ~70 items (40 answerable, 15 unanswerable, 15 hard). Treat `n` below as a caveat on every number, not a footnote — a metric on 2-10 cases is a smoke test, not a claim.

| Metric | Score | Target | n | Status |
|---|---|---|---|---|
| Retrieval recall@8 | n/a | ≥ 90% | 0 | n/a |
| Faithfulness (LLM-as-judge) | n/a | ≥ 90% | 0 | n/a |
| Citation precision | n/a | ≥ 90% | 0 | n/a |
| Refusal accuracy | n/a | ≥ 93% | 0 | n/a |
| Hallucination rate | n/a | ≤ 5% | 0 | n/a |

p95 time-to-first-token: n/a (target < 1.5s)

p95 total query latency: n/a

## Methodology

- **Retrieval recall@8** — for every golden item with a ground-truth clause (or page, when no clause number applies), did hybrid search's top-8 chunks (vector + lexical, RRF-fused) include it? Unanswerable items have no ground-truth clause and are excluded.
- **Faithfulness / citation precision / hallucination rate** — the judge splits each non-refusal answer into atomic claims and checks each one against (a) the full retrieved set (`supported_by_context`, drives faithfulness and hallucination rate) and (b) specifically the clause(s) the answer cited for that claim (`supported_by_citation`, drives citation precision). All three are pooled over every claim in the run, not averaged per-case.
- **Refusal accuracy** — of the unanswerable golden items, the fraction where the system actually produced the refusal message.
- **Hallucination rate** — fraction of claims across the full run that are not supported by anything in the retrieved context (unlike citation precision, this ignores which clause was cited).

## Judge

The judge is OpenAI `gpt-4o-mini` — a different model family from the generator (Anthropic Claude). A model is a poor judge of its own answers: it tends to share the same blind spots that produced the answer in the first place. Grading with a different family means the judge's failure modes don't systematically line up with the generator's.

## Before / after

**Before/after — hybrid retrieval (CP4).** On the hand-checked MRR comparison set (`tests/retrieval/data/mrr_comparison_cases.py`), vector-only search scores MRR ≈ 0.83 and lexical-only ≈ 0.41 (Postgres FTS is currently weak on currency tokens like "$40" and on AND-joined filler-word queries). Fusing both with Reciprocal Rank Fusion ties the best single retriever (hybrid ≈ 0.83) rather than being dragged down by the weaker one. The win here is robustness, not a raw MRR jump — lexical isn't yet strong enough to out-rank vector on any case in that set, so a genuine hybrid *win* is the next retrieval improvement to chase once lexical search is tuned.

## Per-case results

| id | type | retrieval hit | refusal correct | faithfulness | citation precision | ttft (s) |
|---|---|---|---|---|---|---|
