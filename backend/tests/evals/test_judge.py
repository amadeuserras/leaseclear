from __future__ import annotations

from types import SimpleNamespace

import pytest

from leaseclear.evals import judge


class _FakeClient:
    def __init__(self, content: str) -> None:
        async def create(**_kwargs: object) -> SimpleNamespace:
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

        self.chat = SimpleNamespace(completions=SimpleNamespace(create=create))


async def test_judge_answer_parses_claims(monkeypatch: pytest.MonkeyPatch) -> None:
    raw = (
        '{"claims": [{"text": "Rent is $1,875.00", "cited_ids": ["[lease §3]"], '
        '"supported_by_citation": true, "supported_by_context": true}]}'
    )
    monkeypatch.setattr(judge, "_get_client", lambda: _FakeClient(raw))

    verdict = await judge.judge_answer(
        "What is rent?", "Rent is $1,875.00 [lease §3]", [], []
    )

    assert verdict.faithfulness == 1.0
    assert verdict.citation_precision == 1.0
