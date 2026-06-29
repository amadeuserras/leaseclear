from __future__ import annotations

from pathlib import Path
from typing import cast

import fitz

from leaseclear.types import PageText, ParsedDocument, UploadDocument


def parse_document(upload: UploadDocument) -> ParsedDocument:
    source = Path(upload.path)
    pages: list[PageText] = []

    with fitz.open(source) as doc:
        for index in range(doc.page_count):
            page = doc[index]
            text = cast(str, page.get_text("text")).strip()
            pages.append(PageText(page_number=index + 1, text=text))

    return ParsedDocument(filename=upload.filename, pages=pages)
