#!/usr/bin/env bash
set -euo pipefail

COMPOSE_FILE="tests/phase02/docker-compose.postgres.yml"
PROJECT_NAME="eduboost-phase2-verification"
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
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-test-encryption-key}"
export DATABASE_URL="postgresql+asyncpg://phase2:phase2@127.0.0.1:55434/eduboost_phase2_test"
export PHASE2_TEST_DATABASE_URL="$DATABASE_URL"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic

# Prove the supported upgrade path, then prove Phase 2 downgrade/upgrade recovery.
"$PYTHON_BIN" -m alembic upgrade 20260614_0900_p1_validation
"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m pytest -q tests/phase02
"$PYTHON_BIN" -m alembic downgrade 20260614_0900_p1_validation
"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m pytest -q tests/phase02/test_phase2_postgres_integration.py
