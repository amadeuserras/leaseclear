from __future__ import annotations

from leaseclear.types import ChunkBase, GenerationResult, ValidationResult


def is_refusal(result: GenerationResult, refusal_message: str) -> bool:
    """Whether `result` is a refusal.

    The prompt demands the bare refusal sentence, but the model sometimes wraps
    it in an explanation, so a strict equality check misses genuine refusals.
    A cited answer that merely quotes the sentence (e.g. for one sub-question)
    is still an answer, hence the no-citations condition.
    """
    return refusal_message in result.answer and not result.citations


def validate(
    result: GenerationResult,
    chunks: list[ChunkBase],
    refusal_message: str,
) -> ValidationResult:
    if is_refusal(result, refusal_message):
        return ValidationResult(passed=True, phantom_ids=[], uncited_claims=False)

    valid_ids = {c.citation_id for c in chunks}
    phantom_ids = [c.id for c in result.citations if c.id not in valid_ids]
    uncited_claims = not result.citations and bool(result.answer.strip())
    passed = not phantom_ids and not uncited_claims

    return ValidationResult(
        passed=passed,
        phantom_ids=phantom_ids,
        uncited_claims=uncited_claims,
    )
