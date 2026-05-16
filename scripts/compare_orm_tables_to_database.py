#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import create_async_engine


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class SchemaComparison:
    orm_tables: set[str]
    database_tables: set[str]
    missing_in_database: set[str]
    extra_in_database: set[str]


def _import_model_modules() -> None:
    modules = [
        "app.models",
        "app.models.diagnostic_item",
        "app.models.item_exposure",
    ]
    for module in modules:
        try:
            __import__(module)
        except Exception as exc:
            print(f"warning: could not import {module}: {type(exc).__name__}: {exc}")


def collect_orm_tables() -> set[str]:
    _import_model_modules()
    from app.core.database import Base

    return set(Base.metadata.tables)


async def collect_database_tables(database_url: str) -> set[str]:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            def inspect_tables(sync_connection: Any) -> set[str]:
                inspector = inspect(sync_connection)
                return set(inspector.get_table_names())

            return await connection.run_sync(inspect_tables)
    finally:
        await engine.dispose()


async def compare(database_url: str, ignore_tables: set[str] | None = None) -> SchemaComparison:
    orm_tables = collect_orm_tables()
    database_tables = await collect_database_tables(database_url)
    
    ignored = ignore_tables or set()
    filtered_db_tables = database_tables - ignored
    
    return SchemaComparison(
        orm_tables=orm_tables,
        database_tables=database_tables,
        missing_in_database=orm_tables - filtered_db_tables,
        extra_in_database=filtered_db_tables - orm_tables,
    )


def _print_table_list(title: str, values: set[str]) -> None:
    print(title)
    if not values:
        print("- none")
        return
    for value in sorted(values):
        print(f"- {value}")


async def _async_main(args: argparse.Namespace) -> int:
    orm_tables = collect_orm_tables()
    _print_table_list("ORM tables", orm_tables)

    if not args.database_url:
        print("DATABASE_URL not supplied; database comparison skipped.")
        return 1 if args.require_db else 0

    ignore = {"alembic_version"}
    if args.ignore_consolidation_tables:
        ignore.update({
            "consent_records",
            "correction_requests",
            "data_export_requests",
            "erasure_requests",
            "restriction_requests",
        })

    comparison = await compare(args.database_url, ignore_tables=ignore)
    _print_table_list("Database tables", comparison.database_tables)
    if ignore & comparison.database_tables:
        _print_table_list("Ignored database tables", ignore & comparison.database_tables)
    
    _print_table_list("Missing in database", comparison.missing_in_database)
    _print_table_list("Extra in database", comparison.extra_in_database)

    if args.fail_on_drift and (comparison.missing_in_database or comparison.extra_in_database):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL", ""))
    parser.add_argument("--require-db", action="store_true")
    parser.add_argument("--fail-on-drift", action="store_true")
    parser.add_argument("--ignore-consolidation-tables", action="store_true", help="Ignore known unmapped POPIA/Consolidation tables")
    args = parser.parse_args()

    return asyncio.run(_async_main(args))


if __name__ == "__main__":
    raise SystemExit(main())
