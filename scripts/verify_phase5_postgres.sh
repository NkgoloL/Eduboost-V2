#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
COMPOSE_FILE="tests/phase05/docker-compose.postgres.yml"
PROJECT_NAME="eduboost-phase5-verification"
PYTHON_BIN="${PYTHON_BIN:-.venv/bin/python}"
[[ -x "$PYTHON_BIN" ]] || PYTHON_BIN="$(command -v python3 || true)"
[[ -n "$PYTHON_BIN" ]] || { echo "Python 3 is required" >&2; exit 2; }

docker compose version >/dev/null
cleanup() {
  docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT
cleanup

docker compose -p "$PROJECT_NAME" -f "$COMPOSE_FILE" up -d --wait

export APP_ENV=test ENVIRONMENT=test
export JWT_SECRET="${JWT_SECRET:-test-jwt-secret-test-jwt-secret-1234}"
export ENCRYPTION_KEY="${ENCRYPTION_KEY:-MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=}"
export DATABASE_URL="postgresql+asyncpg://phase5:phase5@127.0.0.1:55438/eduboost_phase5_test"
export PHASE1_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE2_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE3_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE4_TEST_DATABASE_URL="$DATABASE_URL"
export PHASE5_TEST_DATABASE_URL="$DATABASE_URL"
export SEMANTIC_EMBEDDING_PROVIDER=deterministic
export CONTENT_CONSENSUS_THRESHOLD=3
export LLM_PROVIDER=deterministic

printf '\n[1/6] Existing-environment upgrade from Phase 4 head\n'
"$PYTHON_BIN" -m alembic upgrade 20260615_0900_p4_irt_quality
"$PYTHON_BIN" -m alembic upgrade head

printf '\n[2/6] Phase 5 PostgreSQL schema, idempotency, privacy and service tests\n'
"$PYTHON_BIN" -m pytest -q tests/phase05/test_phase5_postgres_integration.py -W error::RuntimeWarning

printf '\n[3/6] Trigger and constraint proof\n'
"$PYTHON_BIN" - <<'PY'
import asyncio, os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
async def main():
    engine=create_async_engine(os.environ['DATABASE_URL'])
    async with engine.connect() as conn:
        tables=set((await conn.execute(text("""
          SELECT table_name FROM information_schema.tables
          WHERE table_schema='public' AND table_name LIKE 'tutor_%'
        """))).scalars().all())
        assert {'tutor_sessions','tutor_messages','tutor_escalations'} <= tables, tables
        triggers=(await conn.execute(text("SELECT tgname FROM pg_trigger WHERE tgname='trg_tutor_messages_append_only'"))).scalars().all()
        assert triggers == ['trg_tutor_messages_append_only'], triggers
    await engine.dispose()
asyncio.run(main())
print('Phase 5 PostgreSQL contracts present')
PY

printf '\n[4/6] Downgrade/re-upgrade recovery to Phase 4 boundary\n'
"$PYTHON_BIN" -m alembic downgrade 20260615_0900_p4_irt_quality
"$PYTHON_BIN" -m alembic upgrade head
"$PYTHON_BIN" -m pytest -q tests/phase05/test_phase5_postgres_integration.py -W error::RuntimeWarning

printf '\n[5/6] Combined Phase 1-5 PostgreSQL regression\n'
"$PYTHON_BIN" -m pytest -q tests/phase01 tests/phase02 tests/phase03 tests/phase04 tests/phase05 -W error::RuntimeWarning

printf '\n[6/6] Migration and schema integrity\n'
"$PYTHON_BIN" scripts/verify_migration_graph.py
"$PYTHON_BIN" scripts/validate_schema_integrity.py

echo 'PHASE 5 POSTGRESQL VERIFICATION PASSED'
