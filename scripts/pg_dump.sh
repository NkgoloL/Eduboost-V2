#!/usr/bin/env bash
# Wrapper script for pg_dump that uses Docker if system version fails
# Ensures compatibility with PostgreSQL 17.6 (Supabase)

set -e

# Check if system pg_dump works
if command -v pg_dump >/dev/null 2>&1 && pg_dump --version 2>&1 | grep -q "17\."; then
    exec pg_dump "$@"
fi

# Fall back to Docker-based pg_dump 17
echo "System pg_dump failed, using Docker fallback..."
exec docker run --rm -i ghcr.io/postgres/pg_dump:17 "$@"
