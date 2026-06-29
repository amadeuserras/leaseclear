from __future__ import annotations

import uuid

from leaseclear.ingestion.slug import make_document_slug
from leaseclear.types import AssignedDocument, ParsedDocument


def assign_document(parsed: ParsedDocument, taken: set[str]) -> AssignedDocument:
    return AssignedDocument(
        id=uuid.uuid4(),
        slug=make_document_slug(parsed.filename, taken),
        filename=parsed.filename,
        pages=parsed.pages,
    )
