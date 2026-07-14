from __future__ import annotations

import re
import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from leaseclear.types import AssignedDocument, ChunkBase, PageText

# Top-level clause: "12." or "12. Title..."
_TOP_CLAUSE = re.compile(r"^(\d{1,3})\.(?:\s+(.*))?$")

# Dotted clause: "5.1", "5.1 Title...", "5.1.2 ...".
_DOTTED_CLAUSE = re.compile(r"^(\d{1,3}(?:\.\d+)+)(?:\s+(.*))?$")

# Sentence-ending punctuation or the end of the line, if there is none
_TITLE_END = re.compile(r"^([^.:;]*)")

# Bare markers: "3.", "5.1", or "A." with the real text on the next.
_BARE_MARKER = re.compile(r"^(?:\d+\.|\d+(?:\.\d+)+|[A-Z]\.)$")

MAX_CHUNK_CHARS = 2400
_SPLITTERS = ("\n\n", "\n", ". ", " ")

CitationBase = str


@dataclass
class _Chunk:
    clause_number: str | None
    clause_title: str | None
    text: str
    start_page: int
    end_page: int
    index: int = 0
    citation: str = ""


@dataclass
class _Line:
    text: str
    page_number: int


def chunk_documents(documents: Sequence[AssignedDocument]) -> list[ChunkBase]:
    chunks: list[ChunkBase] = []
    for document in documents:
        for raw in _chunk_pages(document.pages):
            chunks.append(
                ChunkBase(
                    id=uuid.uuid4(),
                    document_id=document.id,
                    document_slug=document.slug,
                    text=raw.text,
                    clause_number=raw.clause_number,
                    clause_title=raw.clause_title,
                    start_page=raw.start_page,
                    end_page=raw.end_page,
                    index=raw.index,
                    citation=raw.citation,
                )
            )
    return chunks


def _chunk_pages(pages: list[PageText]) -> list[_Chunk]:
    lines = _flatten_lines(pages)

    chunks: list[_Chunk] = []
    clause: str | None = None
    title: str | None = None
    body: list[str] = []
    start_page: int | None = None
    end_page: int | None = None

    def flush() -> None:
        if body and start_page is not None and end_page is not None:
            chunks.append(
                _Chunk(
                    clause_number=clause,
                    clause_title=title,
                    text="\n".join(body),
                    start_page=start_page,
                    end_page=end_page,
                )
            )

    for line in lines:
        start = _clause_start(line.text)
        if start is not None:
            flush()
            clause, title = start
            body = [line.text]
            start_page = line.page_number
            end_page = line.page_number
        else:
            if start_page is None:
                start_page = line.page_number
            body.append(line.text)
            end_page = line.page_number

    flush()
    result = [piece for chunk in chunks for piece in _split_chunk(chunk)]
    _assign_citations(result)
    for index, chunk in enumerate(result):
        chunk.index = index
    return result


def _flatten_lines(pages: list[PageText]) -> list[_Line]:
    lines: list[_Line] = []
    for page in pages:
        for raw_line in page.text.splitlines():
            text = raw_line.strip()
            if text:
                lines.append(_Line(text=text, page_number=page.page_number))
    return _merge_bare_markers(lines)


def _merge_bare_markers(lines: list[_Line]) -> list[_Line]:
    merged: list[_Line] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if _BARE_MARKER.match(line.text) and i + 1 < len(lines):
            nxt = lines[i + 1]
            merged.append(
                _Line(
                    text=f"{line.text} {nxt.text}",
                    page_number=line.page_number,
                )
            )
            i += 2
            continue
        merged.append(line)
        i += 1
    return merged


def _clause_start(line: str) -> tuple[str, str | None] | None:
    match = _DOTTED_CLAUSE.match(line) or _TOP_CLAUSE.match(line)
    if not match:
        return None

    number = match.group(1)
    rest = (match.group(2) or "").strip()
    if not rest:
        return number, None

    title_match = _TITLE_END.match(rest)
    title = title_match.group(1).strip() if title_match else ""
    return number, (title or None)


def _split_oversized(text: str, max_chars: int) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    for separator in _SPLITTERS:
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


def _split_chunk(chunk: _Chunk) -> list[_Chunk]:
    pieces = _split_oversized(chunk.text, MAX_CHUNK_CHARS)
    return [
        _Chunk(
            clause_number=chunk.clause_number,
            clause_title=chunk.clause_title,
            text=piece,
            start_page=chunk.start_page,
            end_page=chunk.end_page,
        )
        for piece in pieces
    ]


def _citation_base(chunk: _Chunk) -> CitationBase:
    if chunk.clause_number is not None:
        return f"§{chunk.clause_number}"
    return f"p{chunk.start_page}"


def _assign_citations(chunks: list[_Chunk]) -> None:
    groups: dict[CitationBase, list[_Chunk]] = {}
    for chunk in chunks:
        groups.setdefault(_citation_base(chunk), []).append(chunk)

    for base, group in groups.items():
        if len(group) == 1:
            group[0].citation = base
            continue
        for index, chunk in enumerate(group, start=1):
            chunk.citation = f"{base}({index})"
