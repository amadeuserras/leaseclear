# LeaseClear

Residential lease Q&A with **cited answers**, **honest refusals**, and **published eval metrics**.

## Repo layout

- **`backend/`** — Production API: ingestion, retrieval, generation, and evals (FastAPI).
- **`frontend/`** — Web UI for lease Q&A (Next.js).
- **`corpus/`** — `generate.py` builds synthetic lease PDFs from Python data in `data/`; outputs land in `corpus/generated/`.

## Development

### Backend

First time (installs Python 3.12 and deps via [uv](https://docs.astral.sh/uv/)):

```bash
cd backend
uv sync
```

Lint, typecheck, and test:

```bash
cd backend
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pytest
```

Auto-format if `ruff format --check` fails:

```bash
uv run ruff format .
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

`generate.py` plus `models/lease.py` (dataclasses) and `data/` (lease definitions). Each lease generates `corpus/generated/{id}.pdf`.

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

Generate a single lease by id:

```bash
cd corpus
uv run python generate.py syn-baseline
```

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
- **Corpus:** dataclasses, `generate.py`, Jinja template, PyMuPDF
- **Tooling:** uv, ruff, pyright, pytest, GitHub Actions
