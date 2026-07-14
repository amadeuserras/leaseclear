from __future__ import annotations

import re
from pathlib import Path
from typing import cast

import fitz

from leaseclear.types import PageText, ParsedDocument, UploadDocument

_HORIZONTAL_WHITESPACE = re.compile(r"[^\S\n]+")


def _normalize(text: str) -> str:
    lines = text.split("\n")
    cleaned = [_HORIZONTAL_WHITESPACE.sub(" ", line).strip() for line in lines]
    return "\n".join(cleaned)


def parse_document(upload: UploadDocument) -> ParsedDocument:
    source = Path(upload.path)
    pages: list[PageText] = []

    with fitz.open(source) as doc:
        for index in range(doc.page_count):
            page = doc[index]
            text = _normalize(cast(str, page.get_text("text")).strip())
            pages.append(PageText(page_number=index + 1, text=text))

    return ParsedDocument(filename=upload.filename, pages=pages)
