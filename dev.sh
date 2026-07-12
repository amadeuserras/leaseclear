#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "Shutting down…"
  kill "$API_PID" 2>/dev/null || true
  kill "$FRONTEND_PID" 2>/dev/null || true
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

echo "Waiting for API…"
ready=0
for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:8000/health" > /dev/null; then
    ready=1
    break
  fi
  sleep 0.5
done
if [ "$ready" -ne 1 ]; then
  echo "API did not become ready in time." >&2
  exit 1
fi

# 3. Frontend
echo "Starting frontend…"
cd "$ROOT/frontend"
npm run dev &
FRONTEND_PID=$!

echo "Waiting for frontend…"
ready=0
for _ in $(seq 1 60); do
  if curl -sf "http://127.0.0.1:3000" > /dev/null; then
    ready=1
    break
  fi
  sleep 0.5
done
if [ "$ready" -ne 1 ]; then
  echo "Frontend did not become ready in time." >&2
  exit 1
fi

open "http://localhost:3000"

wait "$FRONTEND_PID"
