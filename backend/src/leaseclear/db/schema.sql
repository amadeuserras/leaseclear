-- DEV ONLY: drops all app tables before recreate. Remove before production deploy.

DROP TABLE IF EXISTS logs CASCADE;
DROP TABLE IF EXISTS chunks CASCADE;
DROP TABLE IF EXISTS documents CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE users (
    id UUID PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE documents (
    id UUID PRIMARY KEY,
    -- NULL for system-level ingests (corpus/evals); API uploads always set it.
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    slug TEXT NOT NULL,
    landlord_name TEXT,
    tenant_names TEXT[],
    property_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX documents_user_id_idx ON documents (user_id);

CREATE TABLE chunks (
    id UUID PRIMARY KEY,
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    document_slug TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding vector(1536) NOT NULL,
    clause_number TEXT,
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

-- Supports the ORDER BY text <->> query (word-similarity KNN) in trigram search.
CREATE INDEX chunks_text_trgm_gist_idx
    ON chunks USING gist (text gist_trgm_ops);

CREATE TABLE logs (
    id UUID PRIMARY KEY,
    user_id UUID,
    question TEXT NOT NULL,
    document_ids UUID[],
    chunk_ids_retrieved UUID[] NOT NULL,
    ttft_s REAL,
    total_s REAL,
    input_tokens INT,
    output_tokens INT,
    refused BOOLEAN NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
