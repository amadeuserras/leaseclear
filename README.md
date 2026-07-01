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

Workflow before commit

```bash
uv run ruff check .
uv run ruff format .
uv run pyright
uv run pytest
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

## Evals

`backend/src/leaseclear/evals/` is the eval harness: a golden dataset
(`evals/golden/golden.jsonl`) of answerable, unanswerable, and hard questions,
each run through the real retrieval → generation pipeline and scored on
retrieval recall@8, faithfulness, citation precision, refusal accuracy,
hallucination rate, and TTFT/latency. Faithfulness, citation precision, and
hallucination rate are graded by an LLM judge (OpenAI `gpt-4o-mini`) — a
different model family than the generator (Anthropic Claude), so the judge
isn't grading its own homework.

Every run writes a new timestamped report to **[`metrics/`](metrics/)**
(`metrics/<YYYYMMDD-HHMMSS>.md`) instead of overwriting a single file, so the
numbers over time are the history — sort the directory and the most recent
file is the current state.

- Fast tests (`uv run pytest`) cover the harness itself with no external API
  calls, so they run on every push.
- The real run (`uv run pytest -m eval`, or `uv run python
  scripts/run_evals.py [--limit N]` to also write a report) calls real
  OpenAI and Anthropic APIs against a fully-ingested corpus, so it's on-demand
  / nightly only (`.github/workflows/evals.yml`), not on every push.

## Stack

- **Backend:** FastAPI, PostgreSQL + pgvector, hybrid retrieval (vector + FTS + RRF), Claude generation
- **Frontend:** Next.js, TypeScript, Tailwind
- **Corpus:** dataclasses, `generate.py`, Jinja2 templates, PyMuPDF
- **Tooling:** uv, ruff, pyright, pytest, GitHub Actions
