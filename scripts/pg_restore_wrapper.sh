#!/usr/bin/env bash
# Wrapper script for pg_restore - uses Docker if needed
# Ensures PostgreSQL 17 compatibility with Supabase

set -e

# Check if environment variable is set
if [ -n "$PG_RESTORE_IMAGE" ]; then
    # Use Docker-based pg_restore
    echo "Using Docker-based pg_restore: $PG_RESTORE_IMAGE"
    docker run --rm --workdir /data -v /tmp:/data $PG_RESTORE_IMAGE:latest "$@"
else
    # Fall back to system pg_restore
    echo "Using system pg_restore"
    exec pg_restore "$@"
fi
