from __future__ import annotations

from dataclasses import asdict

from openai import OpenAI

from leaseclear.core.config import settings
from leaseclear.types import ChunkBase, EmbeddedChunk

MODEL = "text-embedding-3-small"


def _get_client() -> OpenAI:
    return OpenAI(api_key=settings.openai_embeddings_api_key)


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = _get_client().embeddings.create(input=texts, model=MODEL)
    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]


def embed_chunks(chunks: list[ChunkBase]) -> list[EmbeddedChunk]:
    embeddings = embed_texts([chunk.text for chunk in chunks])
    return [
        EmbeddedChunk(**asdict(chunk), embedding=embedding)
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]
