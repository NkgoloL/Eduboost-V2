#!/usr/bin/env python3
"""Guarded database restore command.

Dry-run remains the CI default. Non-dry-run execution restores a PostgreSQL dump
with ``pg_restore`` for custom dumps or ``psql`` for SQL files. Production
restore targets require both ``--allow-production-target`` and
``--confirm-restore``.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


REQUIRED_ENV = (
    "DATABASE_URL",
    "BACKUP_ENCRYPTION_KEY",
)

PRODUCTION_NAMES = {"production", "prod"}


@dataclass(frozen=True)
class RestorePreflightResult:
    name: str
    ok: bool
    detail: str


def validate_environment(env: dict[str, str] | None = None) -> list[RestorePreflightResult]:
    values = env if env is not None else os.environ
    results: list[RestorePreflightResult] = []

    for name in REQUIRED_ENV:
        value = values.get(name, "")
        results.append(
            RestorePreflightResult(
                name=name,
                ok=bool(value.strip()),
                detail="present" if value.strip() else "missing",
            )
        )

    return results


def validate_target_environment(target_environment: str, allow_production: bool) -> RestorePreflightResult:
    normalized = target_environment.strip().lower()
    is_production = normalized in PRODUCTION_NAMES
    ok = not is_production or allow_production
    return RestorePreflightResult(
        name="target_environment",
        ok=ok,
        detail="allowed" if ok else "production restore requires --allow-production-target",
    )


def validate_restore_confirmation(target_environment: str, confirm_restore: bool) -> RestorePreflightResult:
    normalized = target_environment.strip().lower()
    if normalized in PRODUCTION_NAMES and not confirm_restore:
        return RestorePreflightResult("confirm_restore", False, "production restore requires --confirm-restore")
    return RestorePreflightResult("confirm_restore", True, "confirmed" if confirm_restore else "not required")


def validate_restore_tool(backup_artifact: str) -> RestorePreflightResult:
    suffix = Path(backup_artifact).suffix.lower()
    tool = "psql" if suffix == ".sql" else "pg_restore"
    path = shutil.which(tool)
    return RestorePreflightResult(tool, bool(path), path or f"{tool} not found on PATH")


def render_plan(backup_artifact: str, target_environment: str, dry_run: bool) -> str:
    mode = "dry-run" if dry_run else "execute"
    lines = [
        "# Database Restore Plan",
        "",
        f"Mode: `{mode}`",
        f"Backup artifact: `{backup_artifact}`",
        f"Target environment: `{target_environment}`",
        "",
        "## Execution Behavior",
        "",
        "- `.dump` artifacts use `pg_restore --clean --if-exists --no-owner --no-privileges`.",
        "- `.sql` artifacts use `psql --set ON_ERROR_STOP=on`.",
        "",
        "## Required Verification",
        "",
        "- verify learner record counts",
        "- verify consent record counts",
        "- verify audit event counts",
        "- run runtime and POPIA consent closure checks",
    ]
    return "\n".join(lines) + "\n"


def build_restore_command(database_url: str, backup_artifact: str) -> list[str]:
    artifact = Path(backup_artifact)
    if artifact.suffix.lower() == ".sql":
        return ["psql", database_url, "--set", "ON_ERROR_STOP=on", "--file", str(artifact)]
    return [
        "pg_restore",
        "--clean",
        "--if-exists",
        "--no-owner",
        "--no-privileges",
        "--dbname",
        database_url,
        str(artifact),
    ]


def execute_restore(*, backup_artifact: str, env: dict[str, str] | None = None) -> list[str]:
    values = env if env is not None else os.environ
    command = build_restore_command(values["DATABASE_URL"], backup_artifact)
    subprocess.run(command, check=True)
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or preflight an EduBoost database restore.")
    parser.add_argument("--backup-artifact", default="artifacts/backups/latest.dump", help="Backup artifact path or ID.")
    parser.add_argument("--target-environment", default="staging", help="Restore target environment.")
    parser.add_argument("--allow-production-target", action="store_true", help="Explicitly allow production restore target.")
    parser.add_argument("--confirm-restore", action="store_true", help="Confirm intentional non-dry-run restore execution.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print restore plan without mutating data.")
    args = parser.parse_args()

    results = validate_environment()
    results.append(validate_target_environment(args.target_environment, args.allow_production_target))
    results.append(validate_restore_confirmation(args.target_environment, args.confirm_restore))
    if not args.dry_run:
        results.append(validate_restore_tool(args.backup_artifact))

    print("Database restore preflight")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: {result.detail}")

    if args.dry_run:
        print(render_plan(args.backup_artifact, args.target_environment, dry_run=True))
        return 0 if all(result.ok or result.name in REQUIRED_ENV for result in results) else 1

    if not all(result.ok for result in results):
        return 1

    if not Path(args.backup_artifact).exists():
        print(f"Backup artifact not found: {args.backup_artifact}")
        return 1

    command = execute_restore(backup_artifact=args.backup_artifact)
    print("Restore command executed: " + " ".join(command[:1] + ["<redacted>"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
