from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from families.complex.data import (
    evergreen_terrace_4b,
    lakeview_drive_12c,
    oak_street_2a,
)
from families.complex.model import ComplexLease
from render import render_document
from themes import THEMES

if TYPE_CHECKING:
    from doc_meta import DocMeta

FAMILY = "complex"
_DIR = Path(__file__).resolve().parent
INSTANCES: list[ComplexLease] = [
    evergreen_terrace_4b.LEASE,
    oak_street_2a.LEASE,
    lakeview_drive_12c.LEASE,
]


def render_html(lease: ComplexLease) -> str:
    ctx = asdict(lease)
    ctx.pop("doc")
    ctx["meta"] = ctx.pop("agreement")
    return render_document(_DIR, THEMES[FAMILY], ctx)


def doc_meta(lease: ComplexLease) -> DocMeta:
    return lease.doc
