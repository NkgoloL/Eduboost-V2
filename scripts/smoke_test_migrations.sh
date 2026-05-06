#!/bin/bash
set -e

echo "Starting migration smoke test..."

# 1. Try to upgrade to head
echo "Upgrading to head..."
alembic upgrade head

# 2. Check current version
echo "Current version:"
alembic current

# 3. Try to downgrade by 1
echo "Testing rollback (downgrade -1)..."
alembic downgrade -1

# 4. Upgrade back to head
echo "Re-upgrading to head..."
alembic upgrade head

echo "Migration smoke test PASSED."
