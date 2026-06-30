#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="tests/phase03/docker-compose.postgres.yml"
PROJECT_NAME="eduboost-phase3-verification"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="python"
fi

cleanup() {
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d --wait

export APP_ENV=test
export ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}" 
export DATABASE_URL="postgresql+asyncpg://phase3:phase3@127.0.0.1:55435/eduboost_phase3_test"
export PHASE1_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE2_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE3_TEST_DATABASE_URL="$DATABASE_URL"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic
export CONTENT_CONSENSUS_THRESHOLD=3

# Prove supported existing-environment upgrade path.
"$PYTHON_BIN" -m alembic upgrade 20260614_1200_p2_retrieval
"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m pytest -q tests/phase03

# Prove Phase 3 downgrade/upgrade recovery without deleting Phase 1/2 data.
"$PYTHON_BIN" -m alembic downgrade 20260614_1200_p2_retrieval
"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m pytest -q tests/phase03/test_phase3_postgres_integration.py

# Final combined Phase 1-3 PostgreSQL regression.
"$PYTHON_BIN" -m pytest -q tests/phase01 tests/phase02 tests/phase03
