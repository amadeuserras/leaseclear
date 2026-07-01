from __future__ import annotations

from types import SimpleNamespace

import pytest

from leaseclear.evals import judge


class _FakeCompletions:
    def __init__(self, content: str) -> None:
        self._content = content

    async def create(self, **_kwargs: object) -> SimpleNamespace:
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self._content))]
        )


class _FakeClient:
    def __init__(self, content: str) -> None:
        self.chat = SimpleNamespace(completions=_FakeCompletions(content))


def _patch_client(monkeypatch: pytest.MonkeyPatch, content: str) -> None:
    monkeypatch.setattr(judge, "_get_client", lambda: _FakeClient(content))


async def test_judge_answer_parses_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = (
        '{"claims": [{"text": "Rent is $1,875.00", "cited_ids": ["[lease §3]"], '
        '"supported_by_citation": true, "supported_by_context": true}]}'
    )
    _patch_client(monkeypatch, raw)

    verdict = await judge.judge_answer(
        "What is rent?", "Rent is $1,875.00 [lease §3]", [], []
    )

    assert len(verdict.claims) == 1
    assert verdict.faithfulness == 1.0
    assert verdict.citation_precision == 1.0


async def test_judge_answer_strips_markdown_fence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = '```json\n{"claims": []}\n```'
    _patch_client(monkeypatch, raw)

    verdict = await judge.judge_answer("q", "a", [], [])

    assert verdict.claims == []
    assert verdict.faithfulness is None
    assert verdict.citation_precision is None


async def test_judge_answer_raises_on_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patch_client(monkeypatch, "not json")

    with pytest.raises(ValueError, match="invalid JSON"):
        await judge.judge_answer("q", "a", [], [])


async def test_judge_answer_flags_unsupported_claim(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    raw = (
        '{"claims": ['
        '{"text": "Pets are allowed", "cited_ids": [], '
        '"supported_by_citation": false, "supported_by_context": false}'
        "]}"
    )
    _patch_client(monkeypatch, raw)

    verdict = await judge.judge_answer("Are pets allowed?", "Pets are allowed.", [], [])

    assert verdict.faithfulness == 0.0
    assert verdict.citation_precision == 0.0
