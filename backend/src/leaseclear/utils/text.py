from __future__ import annotations


def strip_markdown_fence(raw: str) -> str:
    cleaned = raw.strip()
    if not cleaned.startswith("```"):
        return cleaned
    cleaned = cleaned.split("\n", 1)[1]
    cleaned = cleaned.rsplit("```", 1)[0]
    return cleaned.strip()
