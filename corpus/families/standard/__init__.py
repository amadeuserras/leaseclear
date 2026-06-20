from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

from families.standard.data.mission_street_8f import LEASE
from families.standard.model import StandardLease
from render import render_document
from themes import THEMES

if TYPE_CHECKING:
    from doc_meta import DocMeta

FAMILY = "standard"
_DIR = Path(__file__).resolve().parent
INSTANCES: list[StandardLease] = [LEASE]


def render_html(lease: StandardLease) -> str:
    ctx = asdict(lease)
    ctx.pop("doc")
    return render_document(_DIR, THEMES[FAMILY], ctx)


def doc_meta(lease: StandardLease) -> DocMeta:
    return lease.doc
