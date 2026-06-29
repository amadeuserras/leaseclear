from __future__ import annotations

from pathlib import Path

from slugify import slugify


def make_document_slug(filename: str, taken: set[str] | None = None) -> str:
    base = slugify(Path(filename).stem) or "document"
    if taken is None:
        return base

    slug = base
    n = 2
    while slug in taken:
        slug = f"{base}-{n}"
        n += 1
    taken.add(slug)
    return slug
