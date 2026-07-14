from __future__ import annotations

import datetime as dt

from leaseclear.evals.retrieval.pipeline import RetrievalEvalResult


def render_retrieval_md(result: RetrievalEvalResult) -> str:
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# RETRIEVAL EVAL",
        "",
        f"_Generated {generated} by `scripts/run_eval.py --mode retrieval` against "
        f"{result.n_items} golden items with a ground-truth clause "
        "(filter LLM + embeddings; no judge/generation LLMs)._",
        "",
        f"MRR and recall@{result.k} are scored against the golden "
        "`citation_ids` ground truth, with document "
        "pre-filtering per question (same as the generation eval pipeline).",
        "",
        f"| Strategy | MRR | Recall@{result.k} |",
        "|---|---|---|",
    ]
    for score in result.scores:
        lines.append(f"| {score.name} | {score.mrr:.4f} | {score.recall_at_k:.4f} |")
    lines.extend(
        ["", f"Winner: **{result.winner.name}** (MRR {result.winner.mrr:.4f})"]
    )
    return "\n".join(lines)
