#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON_BIN:-$ROOT/.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required." >&2; exit 2; }
command -v docker >/dev/null 2>&1 || { echo "Docker is required." >&2; exit 3; }

PROJECT="${RECONCILIATION_COMPOSE_PROJECT:-eduboost-phases1-7-reconciliation}"
PORT="${RECONCILIATION_POSTGRES_PORT:-55441}"
COMPOSE_FILE="$(mktemp --suffix=.phase-reconciliation.yml)"

cleanup() {
  docker compose -p "$PROJECT" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
  rm -f "$COMPOSE_FILE"
}
trap cleanup EXIT
cleanup

cat > "$COMPOSE_FILE" <<YAML
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: eduboost
      POSTGRES_PASSWORD: reconciliation-test-password
      POSTGRES_DB: eduboost_reconciliation_test
    ports:
      - "${PORT}:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U eduboost -d eduboost_reconciliation_test"]
      interval: 2s
      timeout: 3s
      retries: 30
    tmpfs:
      - /var/lib/postgresql/data
YAML

docker compose -p "$PROJECT" -f "$COMPOSE_FILE" up -d --wait

export APP_ENV=test ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}"
export DATABASE_URL="postgresql+asyncpg://eduboost:reconciliation-test-password@127.0.0.1:${PORT}/eduboost_reconciliation_test"
export RECONCILIATION_TEST_DATABASE_URL="$DATABASE_URL"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic
export CONTENT_CONSENSUS_THRESHOLD=3

printf '\n[1/6] Upgrade from the Phase 7 boundary\n'
"$PYTHON_BIN" -m alembic upgrade 20260615_1800_p7_curriculum
"$PYTHON_BIN" -m alembic upgrade 20260615_2100_p17_reconcile

printf '\n[2/6] Reconciliation schema tests\n'
"$PYTHON_BIN" -W error::RuntimeWarning -m pytest -q \
  tests/reconciliation/test_reconciliation_postgres.py \
  --no-cov

printf '\n[3/6] Direct schema and append-only proof\n'
"$PYTHON_BIN" - <<'PY'
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

async def main():
    engine = create_async_engine(os.environ["DATABASE_URL"])
    async with engine.begin() as conn:
        head = await conn.scalar(text("SELECT version_num FROM alembic_version"))
        assert head == "20260615_2100_p17_reconcile", head
        table = await conn.scalar(text("SELECT to_regclass('public.content_answer_key_verifications')"))
        assert table == "content_answer_key_verifications"
        published = await conn.scalar(text(
            "SELECT count(*) FROM information_schema.columns "
            "WHERE table_name='curriculum_coverage_snapshots' AND column_name='published_total'"
        ))
        assert published == 1
        trigger = await conn.scalar(text(
            "SELECT count(*) FROM pg_trigger WHERE tgname='trg_answer_key_verification_append_only'"
        ))
        assert trigger == 1
    await engine.dispose()

asyncio.run(main())
print("Reconciliation schema and append-only trigger verified")
PY

printf '\n[4/6] Downgrade and re-upgrade recovery\n'
"$PYTHON_BIN" -m alembic downgrade 20260615_1800_p7_curriculum
CURRENT="$("$PYTHON_BIN" -m alembic current)"
echo "$CURRENT"
grep -q '20260615_1800_p7_curriculum' <<<"$CURRENT"
"$PYTHON_BIN" -m alembic upgrade 20260615_2100_p17_reconcile

printf '\n[5/6] Final migration and schema gates\n'
"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" scripts/validate_schema_integrity.py

printf '\n[6/6] Prior Phase 1-7 PostgreSQL regression\n'
if [[ "${RUN_PHASE_POSTGRES_REGRESSION:-1}" == "1" ]]; then
  # Phase 7's verifier recursively executes Phases 1-6 and now uses an isolated port.
  bash scripts/verify_phase7_postgres.sh
else
  echo "RUN_PHASE_POSTGRES_REGRESSION=0: prior phase PostgreSQL gates skipped by operator."
fi

echo 'PHASES 1-7 RECONCILIATION POSTGRESQL VERIFICATION PASSED'
