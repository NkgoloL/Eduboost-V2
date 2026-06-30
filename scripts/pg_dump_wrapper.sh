#!/usr/bin/env bash
# Wrapper script for pg_dump - uses Docker if needed
# Ensures PostgreSQL 17 compatibility with Supabase

set -e

# Check if environment variable is set
if [ -n "$PG_DUMP_IMAGE" ]; then
    # Use Docker-based pg_dump
    echo "Using Docker-based pg_dump: $PG_DUMP_IMAGE"
    docker run --rm --workdir /data -v /tmp:/data $PG_DUMP_IMAGE:latest "$@"
else
    # Fall back to system pg_dump
    echo "Using system pg_dump"
    exec pg_dump "$@"
fi
