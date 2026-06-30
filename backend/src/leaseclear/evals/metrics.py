from __future__ import annotations

from leaseclear.evals.types import AggregateMetrics, EvalResult


def score(result: EvalResult) -> None:
    """Compute automated scores and write them onto the result in place."""
    item = result.item

    if item.clause_label is None:
        result.retrieval_recall = 1.0
    else:
        labels = [c.clause_label for c in result.retrieved_chunks if c.clause_label]
        result.retrieval_recall = 1.0 if item.clause_label in labels else 0.0

    result.refusal_accuracy = 1.0 if result.refused == item.expected_refusal else 0.0

    if item.expected_refusal:
        result.answer_match = 1.0 if result.refused else 0.0
    elif item.expected_answer is None:
        result.answer_match = 1.0
    elif result.refused:
        result.answer_match = 0.0
    else:
        result.answer_match = (
            1.0 if item.expected_answer.casefold() in result.answer.casefold() else 0.0
        )


def aggregate(results: list[EvalResult]) -> AggregateMetrics:
    n = len(results)
    if n == 0:
        return AggregateMetrics(
            count=0,
            retrieval_recall=0.0,
            refusal_accuracy=0.0,
            answer_match=0.0,
            faithfulness=None,
            citation_precision=None,
        )

    faith = [r.faithfulness for r in results if r.faithfulness is not None]
    cit = [r.citation_precision for r in results if r.citation_precision is not None]

    return AggregateMetrics(
        count=n,
        retrieval_recall=sum(r.retrieval_recall for r in results) / n,
        refusal_accuracy=sum(r.refusal_accuracy for r in results) / n,
        answer_match=sum(r.answer_match for r in results) / n,
        faithfulness=sum(faith) / len(faith) if faith else None,
        citation_precision=sum(cit) / len(cit) if cit else None,
    )
