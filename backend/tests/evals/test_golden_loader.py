from __future__ import annotations

from leaseclear.evals.golden.loader import load_golden_items

VALID_TYPES = {"answerable", "unanswerable", "hard"}


def test_golden_dataset_loads() -> None:
    items = load_golden_items()
    assert items


def test_golden_ids_are_unique() -> None:
    ids = [item.id for item in load_golden_items()]
    assert len(ids) == len(set(ids))


def test_golden_items_are_well_formed() -> None:
    for item in load_golden_items():
        assert item.type in VALID_TYPES
        assert item.question.strip()
        if item.expected_refusal:
            assert item.expected_answer is None
        else:
            assert item.expected_answer


def test_unanswerable_items_have_no_ground_truth_clause() -> None:
    for item in load_golden_items():
        if item.type == "unanswerable":
            assert item.expected_refusal is True
            assert item.clause_number is None


def test_answerable_and_hard_items_reference_a_document() -> None:
    for item in load_golden_items():
        if item.type in {"answerable", "hard"}:
            assert item.document_slug is not None
