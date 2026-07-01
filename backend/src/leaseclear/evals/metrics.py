from __future__ import annotations

from leaseclear.evals.types import AggregateMetrics, EvalResult

_STOPWORDS = {
    "a",
    "an",
    "the",
    "of",
    "to",
    "in",
    "on",
    "at",
    "for",
    "and",
    "or",
    "is",
    "are",
    "per",
    "with",
    "by",
    "as",
    "least",
    "up",
    "may",
    "must",
    "be",
    "than",
    "that",
    "this",
}
_STRIP_CHARS = ".,;:!?'\"()*_`"


def _normalize_token(token: str) -> str:
    return token.strip(_STRIP_CHARS).casefold()


def _significant_tokens(text: str) -> set[str]:
    tokens = {_normalize_token(t) for t in text.split()}
    return {t for t in tokens if t and t not in _STOPWORDS}


def _answer_matches(expected: str, answer: str) -> bool:
    """Loose match: exact substring, or every significant word/number in the
    expected answer shows up somewhere in the generated answer. This avoids
    penalizing correct answers for cosmetic differences (extra detail,
    "twenty-four (24)" vs "24", markdown formatting, etc.)."""
    if expected.casefold() in answer.casefold():
        return True
    expected_tokens = _significant_tokens(expected)
    if not expected_tokens:
        return False
    return expected_tokens.issubset(_significant_tokens(answer))


def score(result: EvalResult) -> None:
    """Compute automated scores and write them onto the result in place."""
    item = result.item

    if item.clause_number is None:
        result.retrieval_recall = 1.0
    else:
        numbers = [c.clause_number for c in result.retrieved_chunks if c.clause_number]
        result.retrieval_recall = 1.0 if item.clause_number in numbers else 0.0

    result.refusal_accuracy = 1.0 if result.refused == item.expected_refusal else 0.0

    if item.expected_refusal:
        result.answer_match = 1.0 if result.refused else 0.0
    elif item.expected_answer is None:
        result.answer_match = 1.0
    elif result.refused:
        result.answer_match = 0.0
    else:
        result.answer_match = (
            1.0 if _answer_matches(item.expected_answer, result.answer) else 0.0
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
