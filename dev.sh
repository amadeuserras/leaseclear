#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "Shutting down…"
  kill "$API_PID" 2>/dev/null || true
  docker compose -f "$ROOT/docker-compose.yml" stop
}
trap cleanup EXIT INT TERM

# 1. Postgres
echo "Starting Postgres…"
docker compose -f "$ROOT/docker-compose.yml" up -d

# 2. API
echo "Starting API…"
cd "$ROOT/backend"
uv run uvicorn leaseclear.api.main:app --reload --port 8000 &
API_PID=$!

# 3. Frontend
echo "Starting frontend…"
cd "$ROOT/frontend"
npm run dev
