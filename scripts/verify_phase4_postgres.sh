#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMPOSE_FILE="tests/phase04/docker-compose.postgres.yml"
PROJECT_NAME="eduboost-phase4-verification"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then PYTHON_BIN="python3"; fi

cleanup() {
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d --wait

export APP_ENV=test ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}"
export DATABASE_URL="postgresql+asyncpg://phase4:phase4@127.0.0.1:55437/eduboost_phase4_test"
export PHASE1_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE2_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE3_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE4_TEST_DATABASE_URL="$DATABASE_URL"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic
export CONTENT_CONSENSUS_THRESHOLD=3

printf '\n[1/5] Existing-environment upgrade from Phase 3 head\n'
"$PYTHON_BIN" -m alembic upgrade 20260614_1500_p3_consensus
"$PYTHON_BIN" -m alembic upgrade head

printf '\n[2/5] Phase 4 PostgreSQL schema and constraint tests\n'
"$PYTHON_BIN" -m pytest -q tests/phase04 -W error::RuntimeWarning

printf '\n[3/5] Downgrade/upgrade recovery to Phase 3 boundary\n'
"$PYTHON_BIN" -m alembic downgrade 20260614_1500_p3_consensus
"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m pytest -q tests/phase04/test_phase4_postgres_integration.py

printf '\n[4/5] Append-only trigger proof\n'
"$PYTHON_BIN" - <<'PY'
import asyncio, os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
async def main():
    engine=create_async_engine(os.environ['DATABASE_URL'])
    async with engine.connect() as conn:
        names=(await conn.execute(text("SELECT tgname FROM pg_trigger WHERE tgname='trg_irt_calibration_events_append_only'"))).scalars().all()
        assert names == ['trg_irt_calibration_events_append_only']
    await engine.dispose()
asyncio.run(main())
print('Append-only IRT calibration event trigger exists')
PY

printf '\n[5/5] Combined Phase 1-4 PostgreSQL regression\n'
"$PYTHON_BIN" -m pytest -q tests/phase01 tests/phase02 tests/phase03 tests/phase04 -W error::RuntimeWarning

echo 'PHASE 4 POSTGRESQL VERIFICATION PASSED'
