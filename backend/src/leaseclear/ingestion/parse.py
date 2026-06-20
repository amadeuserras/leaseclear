from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

import fitz


@dataclass
class PageText:
    page_number: int
    text: str


@dataclass
class ParsedDocument:
    source: Path
    pages: list[PageText]

    @property
    def page_count(self) -> int:
        return len(self.pages)

    @property
    def full_text(self) -> str:
        return "\n\n".join(page.text for page in self.pages if page.text)


def parse_pdf(path: Path | str) -> ParsedDocument:
    source = Path(path)
    pages: list[PageText] = []

    with fitz.open(source) as doc:
        for index in range(doc.page_count):
            page = doc[index]
            text = cast(str, page.get_text("text")).strip()
            pages.append(PageText(page_number=index + 1, text=text))

    return ParsedDocument(source=source.resolve(), pages=pages)
