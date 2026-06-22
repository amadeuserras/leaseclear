from __future__ import annotations

from leaseclear.types import GenerationResult, LabelledChunk, ValidationResult


def validate(
    result: GenerationResult,
    chunks: list[LabelledChunk],
) -> ValidationResult:
    if result.refusal:
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
