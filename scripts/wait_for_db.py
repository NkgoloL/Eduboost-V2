#!/usr/bin/env python3
"""wait_for_db.py — Wait for database to accept connections."""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


def normalize_db_url(url: str) -> str:
    """Normalize sync/async Postgres driver scheme to postgresql+asyncpg."""
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    return url


async def check_postgres(url: str, timeout: int, interval: int) -> bool:
    """Verify postgres is ready by attempting an async query connection."""
    normalized = normalize_db_url(url)
    engine = create_async_engine(normalized)
    elapsed = 0
    while elapsed < timeout:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            return True
        except Exception as e:
            print(f"PostgreSQL not ready yet ({type(e).__name__}: {e}). Retrying in {interval}s...")
            await asyncio.sleep(interval)
            elapsed += interval
    await engine.dispose()
    return False


def check_sqlite(url: str) -> bool:
    """Verify sqlite database file is accessible or check memory."""
    # e.g., sqlite:///:memory: or sqlite:///path/to/db
    if ":memory:" in url:
        return True
    path_str = urlsplit_path_only(url)
    if path_str:
        p = Path(path_str)
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            p.touch(exist_ok=True)
            return True
        except Exception as e:
            print(f"SQLite file path '{p}' is not writeable ({e}).", file=sys.stderr)
            return False
    return True


def urlsplit_path_only(url: str) -> str | None:
    # Quick parse for sqlite path
    for prefix in ("sqlite:///", "sqlite+aiosqlite:///"):
        if url.startswith(prefix):
            return url.removeprefix(prefix)
    return None


async def main() -> int:
    parser = argparse.ArgumentParser(description="Wait for database readiness")
    parser.add_argument("--timeout", type=int, default=60, help="Max time to wait in seconds")
    parser.add_argument("--interval", type=int, default=1, help="Time between retries in seconds")
    parser.add_argument("--optional", action="store_true", help="Do not fail if DATABASE_URL is missing")
    args = parser.parse_args()

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        if args.optional:
            print("DATABASE_URL is not set, but --optional was passed. Exiting 0.")
            return 0
        print("Error: DATABASE_URL environment variable is required.", file=sys.stderr)
        return 1

    if db_url.startswith(("postgresql://", "postgres://", "postgresql+psycopg2://", "postgresql+asyncpg://")):
        ready = await check_postgres(db_url, args.timeout, args.interval)
        if ready:
            print("PostgreSQL is ready.")
            return 0
        else:
            print(f"Error: PostgreSQL did not become ready within {args.timeout}s.", file=sys.stderr)
            return 1

    if db_url.startswith(("sqlite://", "sqlite+aiosqlite://")):
        ready = check_sqlite(db_url)
        if ready:
            print("SQLite database is ready.")
            return 0
        else:
            return 1

    print(f"Unsupported database URL scheme: {db_url}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
