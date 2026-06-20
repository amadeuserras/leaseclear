from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from doc_meta import DocMeta, doc_id
from families import complex, simple, standard
from themes import THEMES, PdfTheme

RenderFn = Callable[[Any], str]
DocMetaFn = Callable[[Any], DocMeta]


@dataclass(frozen=True)
class FamilySpec:
    name: str
    instances: tuple[Any, ...]
    render_html: RenderFn
    doc_meta: DocMetaFn
    theme: PdfTheme


FAMILIES: tuple[FamilySpec, ...] = (
    FamilySpec(
        name=simple.FAMILY,
        instances=tuple(simple.INSTANCES),
        render_html=simple.render_html,
        doc_meta=simple.doc_meta,
        theme=THEMES[simple.FAMILY],
    ),
    FamilySpec(
        name=standard.FAMILY,
        instances=tuple(standard.INSTANCES),
        render_html=standard.render_html,
        doc_meta=standard.doc_meta,
        theme=THEMES[standard.FAMILY],
    ),
    FamilySpec(
        name=complex.FAMILY,
        instances=tuple(complex.INSTANCES),
        render_html=complex.render_html,
        doc_meta=complex.doc_meta,
        theme=THEMES[complex.FAMILY],
    ),
)

ALL: list[Any] = [instance for family in FAMILIES for instance in family.instances]

BY_ID: dict[str, tuple[FamilySpec, Any]] = {
    doc_id(family.name, family.doc_meta(instance).name): (family, instance)
    for family in FAMILIES
    for instance in family.instances
}

BY_FAMILY: dict[str, FamilySpec] = {family.name: family for family in FAMILIES}
