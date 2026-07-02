from __future__ import annotations

from leaseclear.evals.golden.loader import load_golden_items


def test_golden_dataset_loads() -> None:
    items = load_golden_items()
    assert items
    assert all(item.question for item in items)
