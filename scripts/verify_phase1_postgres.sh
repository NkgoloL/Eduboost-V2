#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is required for the disposable PostgreSQL verification." >&2
  exit 2
fi
if ! docker compose version >/dev/null 2>&1; then
  echo "ERROR: Docker Compose v2 is required." >&2
  exit 2
fi

COMPOSE_FILE="tests/phase01/docker-compose.postgres.yml"
PROJECT_NAME="eduboost-phase1-test"
DATABASE_URL="postgresql+asyncpg://eduboost:phase1-test-password@127.0.0.1:55432/eduboost_phase1_test"

cleanup() {
  docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup
docker compose -p "${PROJECT_NAME}" -f "${COMPOSE_FILE}" up -d --wait

DATABASE_URL="${DATABASE_URL}" python -m alembic upgrade head
DATABASE_URL="${DATABASE_URL}" \
PHASE1_TEST_DATABASE_URL="${DATABASE_URL}" \
  python -m pytest -q tests/phase01 --disable-warnings

DATABASE_URL="${DATABASE_URL}" python -m alembic current
