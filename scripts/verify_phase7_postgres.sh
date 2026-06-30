#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required." >&2; exit 3; }

COMPOSE_FILE="tests/phase07/docker-compose.postgres.yml"
PROJECT="eduboost-phase7-verification"
PHASE7_POSTGRES_PORT="${PHASE7_POSTGRES_PORT:-55439}"
DATABASE_URL="postgresql+asyncpg://eduboost:phase7-test-password@127.0.0.1:${PHASE7_POSTGRES_PORT}/eduboost_phase7_test"
export PHASE7_TEST_DATABASE_URL="$DATABASE_URL"
export DATABASE_URL

cleanup() {
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

export PHASE7_POSTGRES_PORT
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" up -d

for _ in $(seq 1 60); do
  if docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres \
    pg_isready -U eduboost -d eduboost_phase7_test >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres \
  pg_isready -U eduboost -d eduboost_phase7_test >/dev/null

echo "== Upgrade to Phase 6 boundary =="
"$PYTHON_BIN" -m alembic upgrade 20260615_1500_p6_ai_ops

echo "== Upgrade to Phase 7 head =="
"$PYTHON_BIN" -m alembic upgrade 20260615_1800_p7_curriculum

echo "== Phase 7 PostgreSQL tests =="
"$PYTHON_BIN" -W error::RuntimeWarning -m pytest -q \
  tests/phase07/test_phase7_postgres_integration.py \
  --no-cov

echo "== Downgrade boundary =="
"$PYTHON_BIN" -m alembic downgrade 20260615_1500_p6_ai_ops

CURRENT="$("$PYTHON_BIN" -m alembic current)"
echo "$CURRENT"
grep -q '20260615_1500_p6_ai_ops' <<<"$CURRENT"

echo "== Re-upgrade Phase 7 =="
"$PYTHON_BIN" -m alembic upgrade 20260615_1800_p7_curriculum

CURRENT="$("$PYTHON_BIN" -m alembic current)"
echo "$CURRENT"
grep -q '20260615_1800_p7_curriculum' <<<"$CURRENT"

echo "== Prior-phase PostgreSQL regressions =="
for phase in 1 2 3 4 5 6; do
  script="scripts/verify_phase${phase}_postgres.sh"
  [[ -f "$script" ]] || { echo "Missing $script" >&2; exit 4; }
  if [[ "$phase" == "4" ]]; then
    PHASE4_POSTGRES_PORT=55438 bash "$script"
  else
    bash "$script"
  fi
done

echo "== Final migration and schema gates =="
"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" scripts/validate_schema_integrity.py

echo "PHASE 7 POSTGRESQL VERIFICATION PASSED"
