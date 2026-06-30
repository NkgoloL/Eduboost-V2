#!/usr/bin/env bash
set -euo pipefail

ROOT="${ROOT:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required." >&2; exit 3; }

COMPOSE_FILE="tests/phase02r/docker-compose.postgres.yml"
PROJECT="eduboost-phase02r-verification"
PHASE02R_POSTGRES_PORT="${PHASE02R_POSTGRES_PORT:-55440}"
DATABASE_URL="postgresql+asyncpg://eduboost:phase02r-test-password@127.0.0.1:${PHASE02R_POSTGRES_PORT}/eduboost_phase02r_test"
export PHASE02R_POSTGRES_PORT DATABASE_URL
export PHASE02R_TEST_DATABASE_URL="$DATABASE_URL"
export APP_ENV=test ENVIRONMENT=test

cleanup() {
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker compose -p "$PROJECT" -f "$COMPOSE_FILE" up -d
for _ in $(seq 1 60); do
  if docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres \
    pg_isready -U eduboost -d eduboost_phase02r_test >/dev/null 2>&1; then
    break
  fi
  sleep 1
done
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres \
  pg_isready -U eduboost -d eduboost_phase02r_test >/dev/null

echo "== Upgrade from the Phase 1-7 reconciliation head =="
"$PYTHON_BIN" -m alembic upgrade 20260615_2100_p17_reconcile
"$PYTHON_BIN" -m alembic upgrade 20260616_1200_phase02r_authority

echo "== Phase 2R PostgreSQL tests =="
"$PYTHON_BIN" -W error::RuntimeWarning -m pytest -q \
  tests/phase02r/test_phase02r_postgres_integration.py --no-cov

echo "== Load real Gate 2R.1 authority and rights records =="
"$PYTHON_BIN" scripts/curriculum/load_phase02r_authority_records.py \
  --download-missing \
  --json

echo "== Downgrade and re-upgrade =="
"$PYTHON_BIN" -m alembic downgrade 20260615_2100_p17_reconcile
CURRENT="$($PYTHON_BIN -m alembic current)"
echo "$CURRENT"
grep -q '20260615_2100_p17_reconcile' <<<"$CURRENT"
"$PYTHON_BIN" -m alembic upgrade 20260616_1200_phase02r_authority
CURRENT="$($PYTHON_BIN -m alembic current)"
echo "$CURRENT"
grep -q '20260616_1200_phase02r_authority' <<<"$CURRENT"

"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" scripts/validate_schema_integrity.py
"$PYTHON_BIN" scripts/validate_phase02r_authority_schema.py

echo "PHASE 02R GATE 2R.1 POSTGRESQL VERIFICATION PASSED"
