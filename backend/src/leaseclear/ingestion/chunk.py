from __future__ import annotations

import re
from dataclasses import dataclass

from leaseclear.ingestion.parse import PageText, ParsedDocument

SUB_CLAUSE_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
TOP_CLAUSE_LINE = re.compile(r"^(\d+)\.\s+(.*)$")
TITLE = re.compile(r"^([A-Z][A-Z\s/&,\-']+?)\.(?:\s|$)")

MAX_CHUNK_CHARS = 2400
SPLITTERS = ("\n\n", "\n", ". ", " ")


@dataclass
class Chunk:
    text: str
    clause_label: str
    page_number: int


@dataclass
class _Section:
    clause_label: str
    page_number: int
    lines: list[tuple[int, str]]


def chunk_document(document: ParsedDocument) -> list[Chunk]:
    sections = _split_into_sections(document.pages)
    chunks: list[Chunk] = []
    for section in sections:
        chunks.extend(_section_to_chunks(section))
    return chunks


def _split_into_sections(pages: list[PageText]) -> list[_Section]:
    sections: list[_Section] = []
    current: _Section | None = None

    for page in pages:
        if not page.text:
            continue
        for line in page.text.splitlines():
            clause = _parse_clause_start(line)
            if clause is not None:
                if current is not None:
                    sections.append(current)
                num, rest = clause
                current = _Section(
                    clause_label=_clause_label(num, rest),
                    page_number=page.page_number,
                    lines=[(page.page_number, line)],
                )
                continue

            if current is None:
                current = _Section(
                    clause_label="",
                    page_number=page.page_number,
                    lines=[(page.page_number, line)],
                )
            else:
                current.lines.append((page.page_number, line))

    if current is not None:
        sections.append(current)

    return sections


def _section_to_chunks(section: _Section) -> list[Chunk]:
    text = "\n".join(line for _, line in section.lines).strip()
    if not text:
        return []

    pieces = _split_oversized(text, MAX_CHUNK_CHARS)
    chunks: list[Chunk] = []
    for index, piece in enumerate(pieces):
        page_number = _page_for_piece(section.lines, index, pieces)
        body = piece if index == 0 else _prepend_label(piece, section.clause_label)
        chunks.append(
            Chunk(
                text=body,
                clause_label=section.clause_label,
                page_number=page_number,
            )
        )
    return chunks


def _page_for_piece(
    lines: list[tuple[int, str]],
    piece_index: int,
    pieces: list[str],
) -> int:
    if piece_index == 0:
        return lines[0][0]

    offset = sum(len(pieces[i]) for i in range(piece_index))
    consumed = 0
    for page_number, line in lines:
        line_len = len(line) + 1
        if consumed + line_len > offset:
            return page_number
        consumed += line_len
    return lines[-1][0]


def _parse_clause_start(line: str) -> tuple[str, str] | None:
    sub_match = SUB_CLAUSE_LINE.match(line)
    if sub_match:
        return sub_match.group(1), sub_match.group(2)
    top_match = TOP_CLAUSE_LINE.match(line)
    if top_match:
        return top_match.group(1), top_match.group(2)
    return None


def _clause_label(num: str, rest: str) -> str:
    title_match = TITLE.match(rest)
    if title_match:
        return f"{num}. {title_match.group(1).strip()}"
    return num


def _prepend_label(body: str, label: str) -> str:
    if not label:
        return body
    return f"{label}\n\n{body}"


def _split_oversized(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    for separator in SPLITTERS:
        split_at = text.rfind(separator, 0, max_chars)
        if split_at <= 0:
            continue
        head = text[:split_at].strip()
        tail = text[split_at + len(separator) :].strip()
        if not head:
            continue
        return [head, *_split_oversized(tail, max_chars)]

    head = text[:max_chars].strip()
    tail = text[max_chars:].strip()
    if not head:
        return _split_oversized(tail, max_chars)
    return [head, *_split_oversized(tail, max_chars)]
