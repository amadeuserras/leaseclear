from __future__ import annotations

import json
from pathlib import Path

from leaseclear.types import EmbeddedChunk

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "seed_corpus.json"


def load_seed_corpus() -> list[EmbeddedChunk]:
    data = json.loads(FIXTURE.read_text())
    return [EmbeddedChunk(**chunk) for chunk in data["chunks"]]


def load_query_embeddings() -> dict[str, list[float]]:
    data = json.loads(FIXTURE.read_text())
    return data["query_embeddings"]
