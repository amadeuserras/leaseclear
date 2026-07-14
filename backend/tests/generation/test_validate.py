from __future__ import annotations

from leaseclear.evals.generation.answer import is_refusal, validate
from leaseclear.generation.prompts import REFUSAL_MESSAGE
from leaseclear.types import Citation, GenerationResult


def test_valid_citation_passes(cited_result, chunks):
    result = validate(cited_result, chunks)
    assert result.passed
    assert result.phantom_ids == []
    assert not result.uncited_claims


def test_phantom_id_fails(chunks):
    bad_result = GenerationResult(
        answer="The fee is $500. [lease §99]",
        citations=[Citation(id="[lease §99]")],
    )
    result = validate(bad_result, chunks)
    assert not result.passed
    assert "[lease §99]" in result.phantom_ids


def test_refusal_always_passes(refusal_result, chunks):
    result = validate(refusal_result, chunks)
    assert result.passed


def test_uncited_answer_fails(chunks):
    bad_result = GenerationResult(
        answer="The rent is $2,875.00.",
        citations=[],
    )
    result = validate(bad_result, chunks)
    assert not result.passed
    assert result.uncited_claims


def test_wrapped_refusal_is_detected(chunks):
    wrapped = GenerationResult(
        answer=(
            "There is no lease clause about this in the provided documents. "
            f'"{REFUSAL_MESSAGE}"'
        ),
        citations=[],
    )
    assert is_refusal(wrapped)
    assert validate(wrapped, chunks).passed


def test_cited_answer_quoting_refusal_is_not_a_refusal(chunks):
    mixed = GenerationResult(
        answer=(f"The rent is $2,875.00. [lease §3] As for parking: {REFUSAL_MESSAGE}"),
        citations=[Citation(id="[lease §3]")],
    )
    assert not is_refusal(mixed)


def test_exact_refusal_is_detected(refusal_result):
    assert is_refusal(refusal_result)
