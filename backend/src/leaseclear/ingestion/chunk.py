from __future__ import annotations

import re
from dataclasses import dataclass

import tiktoken

from leaseclear.ingestion.parse import PageText, ParsedDocument
from leaseclear.types import ParsedChunk

SUB_CLAUSE_LINE = re.compile(r"^(\d+\.\d+)\s+(.*)$")
TOP_CLAUSE_LINE = re.compile(r"^(\d+)\.\s+(.*)$")
TITLE = re.compile(r"^(.+?)\.(?:\s|$)")

MAX_CHUNK_CHARS = 2400
SPLITTERS = ("\n\n", "\n", ". ", " ")
_TOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")


@dataclass
class _Section:
    clause_label: str
    page_number: int
    lines: list[tuple[int, str]]


@dataclass
class _RawChunk:
    text: str
    clause_label: str
    page_number: int


def chunk_document(document: ParsedDocument, document_id: str) -> list[ParsedChunk]:
    sections = _split_into_sections(document.pages)
    raw_chunks: list[_RawChunk] = []
    for section in sections:
        raw_chunks.extend(_section_to_chunks(section))

    full_text = document.full_text
    search_from = 0
    chunks: list[ParsedChunk] = []
    for index, raw in enumerate(raw_chunks, start=1):
        char_start = full_text.find(raw.text, search_from)
        if char_start == -1:
            char_start = search_from
        char_end = char_start + len(raw.text)
        search_from = char_end
        chunks.append(
            ParsedChunk(
                chunk_id=f"{document_id}_chunk-{index:03d}",
                document_id=document_id,
                text=raw.text,
                clause_label=raw.clause_label,
                page_number=raw.page_number,
                char_start=char_start,
                char_end=char_end,
                token_count=_count_tokens(raw.text),
            )
        )
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


def _section_to_chunks(section: _Section) -> list[_RawChunk]:
    text = _section_text(section.lines).strip()
    if not text:
        return []

    pieces = _split_oversized(text, MAX_CHUNK_CHARS)
    chunks: list[_RawChunk] = []
    for index, piece in enumerate(pieces):
        page_number = _page_for_piece(section.lines, index, pieces)
        body = piece if index == 0 else _prepend_label(piece, section.clause_label)
        chunks.append(
            _RawChunk(
                text=body,
                clause_label=section.clause_label,
                page_number=page_number,
            )
        )
    return chunks


def _section_text(lines: list[tuple[int, str]]) -> str:
    if not lines:
        return ""

    parts = [lines[0][1]]
    for index in range(1, len(lines)):
        prev_page = lines[index - 1][0]
        page, line = lines[index]
        separator = "\n\n" if page != prev_page else "\n"
        parts.append(separator + line)
    return "".join(parts)


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


def _count_tokens(text: str) -> int:
    return len(_TOKEN_ENCODER.encode(text))


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
