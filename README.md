# LeaseClear

Residential lease Q&A with **cited answers**, **honest refusals**, and **published eval metrics**.

## Development

Monorepo: `backend/` (Python / FastAPI) and `frontend/` (Next.js).

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

## Stack

- **Backend:** FastAPI, PostgreSQL + pgvector, hybrid retrieval (vector + FTS + RRF), Claude generation
- **Frontend:** Next.js, TypeScript, Tailwind
- **Tooling:** uv, ruff, pyright, pytest, GitHub Actions
