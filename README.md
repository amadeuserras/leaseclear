# LeaseClear

Residential lease Q&A with **cited answers**, **honest refusals**, and **published eval metrics**.

## Repo layout

- **`backend/`** — Production API: ingestion, retrieval, generation, and evals (FastAPI).
- **`frontend/`** — Web UI for lease Q&A (Next.js).
- **`corpus/`** — Builds a synthetic lease PDF into `corpus/generated/`.

## Development

### Backend

```bash
cd backend
```

Run Docker (for PostgreSQL connection, 'Docker Desktop' must be running)


```bash
docker compose up -d
docker compose ps 
docker compose down
```

Run API server

```bash
uv run uvicorn leaseclear.api.main:app --reload --port 8000
```

Test

```bash
uv run pytest                                    
uv run pytest -m real_api                        
uv run pytest -m ""                              
uv run pytest tests/ingestion/test_parse.py      
```

Lint, typecheck:

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
```

### Frontend

First time:

```bash
cd frontend
npm install
```

Dev server (http://localhost:3000):

```bash
npm run dev
```

Production build:

```bash
npm run build
```

Lint:

```bash
npm run lint
```

### Corpus

First time:

```bash
cd corpus
uv sync
```

Generate the full corpus:

```bash
cd corpus
uv run python generate.py
```

Pdf's appear in `/generated`

Lint and typecheck:

```bash
cd corpus
uv run ruff check .
uv run ruff format --check .
uv run pyright
```

## Stack

- **Backend:** FastAPI, PostgreSQL + pgvector, hybrid retrieval (vector + FTS + RRF), Claude generation
- **Frontend:** Next.js, TypeScript, Tailwind
- **Corpus:** dataclasses, `generate.py`, Jinja2 templates, PyMuPDF
- **Tooling:** uv, ruff, pyright, pytest, GitHub Actions
