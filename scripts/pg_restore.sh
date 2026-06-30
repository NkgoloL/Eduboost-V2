#!/usr/bin/env bash
# Wrapper script for pg_restore that uses Docker if system version fails
# Ensures compatibility with PostgreSQL 17.6 (Supabase)

set -e

# Check if system pg_restore works
if command -v pg_restore >/dev/null 2>&1 && pg_restore --version 2>&1 | grep -q "17\."; then
    exec pg_restore "$@"
fi

# Fall back to Docker-based pg_restore 17
echo "System pg_restore failed, using Docker fallback..."
exec docker run --rm -i ghcr.io/postgres/pg_restore:17 "$@"
