from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from families.simple.data.walnut_street_2 import LEASE
from families.simple.model import SimpleLease
from render import render_document
from themes import THEMES

if TYPE_CHECKING:
    from doc_meta import DocMeta

FAMILY = "simple"
_DIR = Path(__file__).resolve().parent
INSTANCES: list[SimpleLease] = [LEASE]


def render_html(lease: SimpleLease) -> str:
    ctx = asdict(lease)
    ctx.pop("doc")
    return render_document(_DIR, THEMES[FAMILY], ctx)


def doc_meta(lease: SimpleLease) -> DocMeta:
    return lease.doc
