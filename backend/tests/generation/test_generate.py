from __future__ import annotations

import pytest

from leaseclear.generation.generate import _parse_response, generate
from leaseclear.generation.prompts import DELIMITER, REFUSAL_MESSAGE
from leaseclear.generation.validate import validate


def test_parse_response_cited_answer() -> None:
    raw = f"""The security deposit is $5,750.00. [lease §4. Security Deposit]
{DELIMITER}
{{"citations": [{{"id": "[lease §4. Security Deposit]", "quote": "$5,750.00"}}], "confidence": 1.0}}"""
    result = _parse_response(raw)
    assert (
        result.answer
        == "The security deposit is $5,750.00. [lease §4. Security Deposit]"
    )
    assert len(result.citations) == 1
    assert result.confidence == 1.0


def test_parse_response_refusal() -> None:
    raw = f"""{REFUSAL_MESSAGE}
{DELIMITER}
{{"citations": [], "confidence": 0.0}}"""
    result = _parse_response(raw)
    assert result.answer == REFUSAL_MESSAGE
    assert result.confidence == 0.0
    assert result.citations == []


def test_parse_response_strips_json_fence() -> None:
    raw = f"""Answer text. [lease §3. Rent]
{DELIMITER}
```json
{{"citations": [{{"id": "[lease §3. Rent]", "quote": "snippet"}}], "confidence": 0.9}}
```"""
    result = _parse_response(raw)
    assert result.answer == "Answer text. [lease §3. Rent]"
    assert result.confidence == 0.9


def test_parse_response_missing_delimiter_raises() -> None:
    with pytest.raises(ValueError, match=DELIMITER):
        _parse_response('{"answer": "no delimiter here"}')


@pytest.mark.real_api
def test_generate_cited_answer(chunks):
    result = generate("How much is the security deposit?", chunks)
    assert result.confidence > 0.5
    assert len(result.citations) > 0
    validation = validate(result, chunks, REFUSAL_MESSAGE)
    assert validation.passed


@pytest.mark.real_api
def test_generate_refusal(chunks):
    result = generate("Are pets allowed?", chunks)
    assert result.answer == REFUSAL_MESSAGE
    assert result.confidence == 0.0
    assert len(result.citations) == 0
