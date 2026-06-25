-- DEV ONLY: drops all app tables before recreate. Remove before production deploy.

DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY,
    filename TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE chunks (
    chunk_id TEXT PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    clause_label TEXT,
    page_number INT,
    char_start INT,
    char_end INT,
    token_count INT,
    text_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', text)) STORED
);

CREATE INDEX chunks_embedding_hnsw_idx
    ON chunks USING hnsw (embedding vector_cosine_ops);

CREATE INDEX chunks_text_tsv_gin_idx
    ON chunks USING gin (text_tsv);

CREATE TABLE logs (
    id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    document_ids TEXT[],
    chunk_ids_retrieved TEXT[] NOT NULL,
    ttft_s REAL,
    total_s REAL,
    input_tokens INT,
    output_tokens INT,
    refused BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
