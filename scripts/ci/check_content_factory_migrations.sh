#!/bin/bash
set -e

# Require DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
  echo "Error: DATABASE_URL environment variable is required."
  exit 1
fi

echo "Safety check on DATABASE_URL..."
python3 -c "
import os, sys
url = os.environ.get('DATABASE_URL', '')
low = url.lower()
if any(x in low for x in ('prod', 'production', 'amazonaws.com', 'azure.com', 'render.com')):
    print('DATABASE_URL looks production-like. Refusing to run migrations on it.')
    sys.exit(1)
print('DATABASE_URL safety check passed.')
"

# ---------------------------------------------------------------------------
# DB readiness: extract host/port from DATABASE_URL and poll pg_isready
# ---------------------------------------------------------------------------
echo "Waiting for database to be ready..."
DB_HOST=$(python3 -c "
import os, re
url = os.environ.get('DATABASE_URL', '')
m = re.search(r'@([^:/]+)', url)
print(m.group(1) if m else 'localhost')
")
DB_PORT=$(python3 -c "
import os, re
url = os.environ.get('DATABASE_URL', '')
m = re.search(r'@[^:/]+:(\d+)', url)
print(m.group(1) if m else '5432')
")
DB_USER=$(python3 -c "
import os, re
url = os.environ.get('DATABASE_URL', '')
m = re.search(r'://([^:@]+)', url)
print(m.group(1) if m else 'postgres')
")

MAX_WAIT=60
WAITED=0
until pg_isready -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -q 2>/dev/null; do
  if [ "${WAITED}" -ge "${MAX_WAIT}" ]; then
    echo "Database was not ready after ${MAX_WAIT}s — aborting."
    exit 1
  fi
  echo "  Waiting for DB at ${DB_HOST}:${DB_PORT} ... (${WAITED}s elapsed)"
  sleep 2
  WAITED=$((WAITED + 2))
done
echo "Database is ready."

# Run alembic current
echo "Checking current migration state..."
alembic current

# Run alembic upgrade head
echo "Upgrading database to head..."
alembic upgrade head

# Verify Content Factory tables/columns exist (using centralized contract)
echo "Verifying Content Factory tables and columns exist..."
python3 -c "
import asyncio
import os
import sys

# Import the single source of truth for table/column contracts
sys.path.insert(0, '.')
from scripts.ci.content_factory_schema_contract import REQUIRED_TABLES, REQUIRED_COLUMNS
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import inspect

async def verify():
    url = os.environ['DATABASE_URL']
    if 'postgresql' in url and '+asyncpg' not in url:
        url = url.replace('postgresql://', 'postgresql+asyncpg://', 1)
    engine = create_async_engine(url)

    def check_schema(conn):
        inspector = inspect(conn)
        tables = inspector.get_table_names()

        for table in REQUIRED_TABLES:
            if table not in tables:
                print(f'Error: Required table {table} does not exist!')
                sys.exit(1)
            print(f'Table verified: {table}')

        for table_name, required_cols in REQUIRED_COLUMNS.items():
            columns = inspector.get_columns(table_name)
            col_names = [c['name'] for c in columns]
            for col in required_cols:
                if col not in col_names:
                    print(f'Error: {table_name} is missing column {col}!')
                    sys.exit(1)
                print(f'Column verified: {table_name}.{col}')

        print('All Content Factory table and column checks PASSED.')

    async with engine.connect() as conn:
        await conn.run_sync(check_schema)
    await engine.dispose()

asyncio.run(verify())
"

# Run alembic downgrade -1
echo "Testing rollback (downgrade -1)..."
alembic downgrade -1

# Run alembic upgrade head again
echo "Re-upgrading to head..."
alembic upgrade head

# ---------------------------------------------------------------------------
# Idempotency check: run alembic upgrade head a second time on an already
# up-to-date database.  Must be a no-op (exit 0, no migrations applied).
# ---------------------------------------------------------------------------
echo "Idempotency check: running upgrade head again on an already-current DB..."
IDEMPOTENCY_OUTPUT=$(alembic upgrade head 2>&1)
echo "${IDEMPOTENCY_OUTPUT}"
if echo "${IDEMPOTENCY_OUTPUT}" | grep -q "Running upgrade"; then
  echo "FAIL: upgrade head applied migrations on an already-current database (not idempotent)."
  exit 1
fi
echo "Idempotency check PASSED — no migrations were applied on second run."

echo "Migration verification completed successfully."
