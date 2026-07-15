from __future__ import annotations

import datetime as dt

from leaseclear.evals.retrieval.pipeline import RetrievalEvalResult, StrategyScore


def _strategy_table(scores: list[StrategyScore], k: int) -> list[str]:
    lines = [f"| Strategy | MRR | Recall@{k} |", "|---|---|---|"]
    for score in scores:
        lines.append(f"| {score.name} | {score.mrr:.4f} | {score.recall_at_k:.4f} |")
    return lines


def render_retrieval_md(result: RetrievalEvalResult) -> str:
    generated = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M UTC")
    mrr_winner = result.mrr_winner
    recall_winner = result.recall_winner

    lines = [
        "# RETRIEVAL EVAL",
        "",
        f"_Generated {generated} by `scripts/run_eval.py --mode retrieval` against "
        f"{result.n_items} golden items with a ground-truth clause "
        "(filter LLM + embeddings; no judge/generation LLMs)._",
        "",
        "## Strategy comparison — with document filter",
        "",
        *_strategy_table(result.filtered_scores, result.k),
        "",
        f"MRR winner: **{mrr_winner.name}** (MRR {mrr_winner.mrr:.4f})",
        f"Recall@{result.k} winner: **{recall_winner.name}** "
        f"(recall {recall_winner.recall_at_k:.4f})",
        "",
        "## Strategy comparison — without document filter",
        "",
        *_strategy_table(result.unfiltered_scores, result.k),
    ]
    return "\n".join(lines)
