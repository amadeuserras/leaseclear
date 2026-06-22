from __future__ import annotations

import pytest

from leaseclear.generation.generate import generate
from leaseclear.generation.validate import validate


@pytest.mark.real_api
def test_generate_cited_answer(chunks):
    result = generate("How much is the security deposit?", chunks)
    assert not result.refusal
    assert result.confidence > 0.5
    assert len(result.citations) > 0
    validation = validate(result, chunks)
    assert validation.passed


@pytest.mark.real_api
def test_generate_refusal(chunks):
    result = generate("Are pets allowed?", chunks)
    assert result.refusal
    assert result.confidence == 0.0
    assert len(result.citations) == 0
