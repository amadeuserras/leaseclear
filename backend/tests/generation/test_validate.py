from __future__ import annotations

from leaseclear.generation.validate import validate
from leaseclear.types import Citation, GenerationResult


def test_valid_citation_passes(cited_result, chunks):
    result = validate(cited_result, chunks)
    assert result.passed
    assert result.phantom_ids == []
    assert not result.uncited_claims


def test_phantom_id_fails(chunks):
    bad_result = GenerationResult(
        answer="The fee is $500. [lease §99. Made Up]",
        citations=[Citation(id="[lease §99. Made Up]", quote="$500")],
        confidence=0.9,
        refusal=False,
    )
    result = validate(bad_result, chunks)
    assert not result.passed
    assert "[lease §99. Made Up]" in result.phantom_ids


def test_refusal_always_passes(refusal_result, chunks):
    result = validate(refusal_result, chunks)
    assert result.passed


def test_uncited_answer_fails(chunks):
    bad_result = GenerationResult(
        answer="The rent is $2,875.00.",
        citations=[],
        confidence=0.8,
        refusal=False,
    )
    result = validate(bad_result, chunks)
    assert not result.passed
    assert result.uncited_claims
