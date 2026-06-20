from __future__ import annotations

from dataclasses import dataclass

from openai import OpenAI

from leaseclear.core.config import settings
from leaseclear.ingestion.chunk import Chunk

EMBEDDING_MODEL = "text-embedding-3-small"

_client = OpenAI(api_key=settings.openai_api_key)


@dataclass
class EmbeddedChunk:
    chunk: Chunk
    embedding: list[float]


def embed_texts(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    response = _client.embeddings.create(input=texts, model=EMBEDDING_MODEL)
    ordered = sorted(response.data, key=lambda item: item.index)
    return [item.embedding for item in ordered]


def embed_chunks(chunks: list[Chunk]) -> list[EmbeddedChunk]:
    embeddings = embed_texts([chunk.text for chunk in chunks])
    return [
        EmbeddedChunk(chunk=chunk, embedding=embedding)
        for chunk, embedding in zip(chunks, embeddings, strict=True)
    ]
