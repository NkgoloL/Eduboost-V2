#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
cd "$ROOT"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required" >&2; exit 2; }
command -v docker >/dev/null || { echo "Docker is required" >&2; exit 3; }

COMPOSE_FILE="tests/phase06/docker-compose.postgres.yml"
PROJECT="eduboost-phase06-${USER:-user}"
DB_URL="postgresql+asyncpg://eduboost:phase6-test-password@127.0.0.1:55446/eduboost_phase6_test"
export DATABASE_URL="$DB_URL"
export PHASE6_TEST_DATABASE_URL="$DB_URL"
export APP_ENV=test ENVIRONMENT=test

cleanup() {
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker compose -p "$PROJECT" -f "$COMPOSE_FILE" up -d
for _ in $(seq 1 45); do
  if docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres pg_isready -U eduboost -d eduboost_phase6_test >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres pg_isready -U eduboost -d eduboost_phase6_test

"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m alembic current

for table in ai_budget_counters ai_usage_reservations ai_usage_events; do
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" exec -T postgres \
    psql -U eduboost -d eduboost_phase6_test -Atc "SELECT to_regclass('public.$table')" | grep -q "$table"
done

"$PYTHON_BIN" -m pytest -q tests/phase06/test_phase6_postgres_integration.py --no-cov -W error::RuntimeWarning

# Explicitly verify Phase 5 boundary downgrade and re-upgrade.
"$PYTHON_BIN" -m alembic downgrade 20260615_1200_p5_tutor
"$PYTHON_BIN" -m alembic upgrade 20260615_1500_p6_ai_ops

# Final focused database gate must not skip.
RESULT="$({ "$PYTHON_BIN" -m pytest -q tests/phase06/test_phase6_postgres_integration.py --no-cov -W error::RuntimeWarning; } 2>&1)"
echo "$RESULT"
if grep -Eqi '[1-9][0-9]* skipped|SKIPPED' <<<"$RESULT"; then
  echo "Unexpected Phase 6 database skip" >&2
  exit 4
fi

# Prior phase database regressions use their own controlled databases.
for script in \
  scripts/verify_phase1_postgres.sh \
  scripts/verify_phase2_postgres.sh \
  scripts/verify_phase3_postgres.sh \
  scripts/verify_phase4_postgres.sh \
  scripts/verify_phase5_postgres.sh; do
  [[ -f "$script" ]] || { echo "Missing prerequisite PostgreSQL verifier: $script" >&2; exit 5; }
  bash "$script"
done

"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" scripts/validate_schema_integrity.py

echo 'PHASE 6 POSTGRESQL VERIFICATION PASSED'
