#!/usr/bin/env bash
set -euo pipefail

# Safe helper to import `scripts/irt_seed_1600.sql` into a Supabase Postgres instance.
# This script intentionally reads credentials from environment variables and
# does NOT embed secrets in the repository.

: "${SUPABASE_PG_HOST:?Set SUPABASE_PG_HOST (e.g. db.xxx.supabase.co)}"
: "${SUPABASE_PG_PORT:=5432}"
: "${SUPABASE_PG_DB:=postgres}"
: "${SUPABASE_PG_USER:?Set SUPABASE_PG_USER}"
: "${SUPABASE_PG_PASSWORD:?Set SUPABASE_PG_PASSWORD (do NOT commit)}"
: "${SEED_SQL:=scripts/irt_seed_1600.sql}"

PSQL_CONN="postgresql://${SUPABASE_PG_USER}:${SUPABASE_PG_PASSWORD}@${SUPABASE_PG_HOST}:${SUPABASE_PG_PORT}/${SUPABASE_PG_DB}"

echo "Importing ${SEED_SQL} into ${SUPABASE_PG_HOST}..."

psql "${PSQL_CONN}" -f "${SEED_SQL}"

echo "Import complete."
