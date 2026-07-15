from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from uuid import UUID

from leaseclear.db.connection import db_session
from leaseclear.evals.db import get_all_documents
from leaseclear.evals.golden.loader import GoldenItem
from leaseclear.evals.retrieval_recall import has_relevance_label, is_relevant_chunk
from leaseclear.filtering.filter import filter_documents
from leaseclear.retrieval import fusion, lexical, trigram, vector
from leaseclear.types import ChunkBase

RETRIEVER_TOP_K = 20
EVAL_TOP_K = 8
MAX_CONCURRENT_ITEMS = 4


@dataclass(frozen=True)
class BaseResults:
    """Raw ranked lists from each retriever for a single question."""

    vector: list[ChunkBase]
    lexical: list[ChunkBase]
    trigram: list[ChunkBase]


Strategy = Callable[[BaseResults], list[ChunkBase]]

STRATEGIES: dict[str, Strategy] = {
    "vector": lambda b: b.vector,
    "lexical": lambda b: b.lexical,
    "trigram": lambda b: b.trigram,
    "vector+lexical": lambda b: fusion.reciprocal_rank_fusion(b.vector, b.lexical),
    "vector+trigram": lambda b: fusion.reciprocal_rank_fusion(b.vector, b.trigram),
    "trigram+lexical": lambda b: fusion.reciprocal_rank_fusion(b.trigram, b.lexical),
    "vector+lexical+trigram": lambda b: fusion.reciprocal_rank_fusion(
        b.vector, b.lexical, b.trigram
    ),
}


@dataclass(frozen=True)
class StrategyScore:
    name: str
    mrr: float
    recall_at_k: float


@dataclass(frozen=True)
class RetrievalEvalResult:
    k: int
    n_items: int
    filtered_scores: list[StrategyScore]
    unfiltered_scores: list[StrategyScore]

    @property
    def mrr_winner(self) -> StrategyScore:
        return max(self.filtered_scores, key=lambda s: s.mrr)

    @property
    def recall_winner(self) -> StrategyScore:
        return max(self.filtered_scores, key=lambda s: s.recall_at_k)

    def unfiltered_score_for(self, name: str) -> StrategyScore:
        return next(s for s in self.unfiltered_scores if s.name == name)


async def _search_base(question: str, document_ids: list[UUID] | None) -> BaseResults:
    return BaseResults(
        vector=await vector.search(
            question, top_k=RETRIEVER_TOP_K, document_ids=document_ids
        ),
        lexical=await lexical.search(
            question, top_k=RETRIEVER_TOP_K, document_ids=document_ids
        ),
        trigram=await trigram.search(
            question, top_k=RETRIEVER_TOP_K, document_ids=document_ids
        ),
    )


def _reciprocal_rank(item: GoldenItem, ranked: list[ChunkBase], k: int) -> float:
    for position, chunk in enumerate(ranked[:k], start=1):
        if is_relevant_chunk(item, chunk):
            return 1.0 / position
    return 0.0


def _hit(item: GoldenItem, ranked: list[ChunkBase], k: int) -> float:
    return float(any(is_relevant_chunk(item, chunk) for chunk in ranked[:k]))


def _mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def _score_strategies(
    scored: list[GoldenItem], bases: list[BaseResults], k: int
) -> list[StrategyScore]:
    reciprocal_ranks: dict[str, list[float]] = {name: [] for name in STRATEGIES}
    hits: dict[str, list[float]] = {name: [] for name in STRATEGIES}

    for item, base in zip(scored, bases, strict=True):
        for name, strategy in STRATEGIES.items():
            ranked = strategy(base)
            reciprocal_ranks[name].append(_reciprocal_rank(item, ranked, k))
            hits[name].append(_hit(item, ranked, k))

    scores = [
        StrategyScore(name, _mean(reciprocal_ranks[name]), _mean(hits[name]))
        for name in STRATEGIES
    ]
    scores.sort(key=lambda s: s.mrr, reverse=True)
    return scores


async def evaluate_retrievers(
    items: list[GoldenItem], *, k: int = EVAL_TOP_K
) -> RetrievalEvalResult:
    scored = [item for item in items if has_relevance_label(item)]

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_ITEMS)

    async def _bases_for(item: GoldenItem) -> tuple[BaseResults, BaseResults]:
        async with semaphore, db_session():
            all_docs = await get_all_documents()
            filtered_ids = await filter_documents(item.question, all_docs)
            filtered_base = await _search_base(item.question, document_ids=filtered_ids)
            unfiltered_base = await _search_base(item.question, document_ids=None)
            return filtered_base, unfiltered_base

    pairs = await asyncio.gather(*(_bases_for(item) for item in scored))
    filtered_bases = [pair[0] for pair in pairs]
    unfiltered_bases = [pair[1] for pair in pairs]

    return RetrievalEvalResult(
        k=k,
        n_items=len(scored),
        filtered_scores=_score_strategies(scored, filtered_bases, k),
        unfiltered_scores=_score_strategies(scored, unfiltered_bases, k),
    )
