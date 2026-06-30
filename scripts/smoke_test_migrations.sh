#!/usr/bin/env bash
set -euo pipefail

echo "Starting migration smoke test..."

# Ensure python is available
PYTHON="${PYTHON:-python3}"

# 1. Wait for database readiness
${PYTHON} scripts/wait_for_db.py --timeout 60 --interval 1

# 2. Try to upgrade to head
echo "Upgrading to head..."
alembic upgrade head

# 3. Check current version
echo "Current version:"
alembic current

# 4. Try to downgrade by 1
echo "Testing rollback (downgrade -1)..."
alembic downgrade -1

# 5. Upgrade back to head
echo "Re-upgrading to head..."
alembic upgrade head

# 6. Idempotency check: running upgrade head again on already upgraded DB
echo "Running idempotency check..."
IDEMPOTENCY_OUTPUT=$(alembic upgrade head 2>&1)
echo "${IDEMPOTENCY_OUTPUT}"
if echo "${IDEMPOTENCY_OUTPUT}" | grep -q "Running upgrade"; then
  echo "FAIL: upgrade head applied migrations on an already-current database (not idempotent)."
  exit 1
fi
echo "Idempotency check PASSED — no migrations were applied on second run."

echo "Migration smoke test PASSED."
