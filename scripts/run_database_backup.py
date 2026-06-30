#!/usr/bin/env python3
"""Guarded database backup command.

Dry-run remains the CI default. Non-dry-run execution now creates a real custom
PostgreSQL dump via ``pg_dump`` and writes a manifest next to the artifact.
Cloud upload is deliberately outside this command until the storage adapter is
reviewed; the Azure settings are still validated so production operators cannot
run with an incomplete backup environment.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


REQUIRED_ENV = (
    "DATABASE_URL",
    "BACKUP_ENCRYPTION_KEY",
    "AZURE_STORAGE_CONNECTION_STRING",
    "AZURE_STORAGE_CONTAINER",
)


@dataclass(frozen=True)
class BackupPreflightResult:
    name: str
    ok: bool
    detail: str


@dataclass(frozen=True)
class BackupExecutionResult:
    artifact: str
    manifest: str
    command: list[str]


def validate_environment(env: dict[str, str] | None = None) -> list[BackupPreflightResult]:
    values = env if env is not None else os.environ
    results: list[BackupPreflightResult] = []

    for name in REQUIRED_ENV:
        value = values.get(name, "")
        results.append(
            BackupPreflightResult(
                name=name,
                ok=bool(value.strip()),
                detail="present" if value.strip() else "missing",
            )
        )

    return results


def validate_backup_tool() -> BackupPreflightResult:
    tool = shutil.which("pg_dump")
    return BackupPreflightResult("pg_dump", bool(tool), tool or "pg_dump not found on PATH")


def render_plan(output_dir: str, dry_run: bool) -> str:
    mode = "dry-run" if dry_run else "execute"
    lines = [
        "# Database Backup Plan",
        "",
        f"Mode: `{mode}`",
        f"Output directory: `{output_dir}`",
        "",
        "## Required Inputs",
        "",
    ]
    for name in REQUIRED_ENV:
        lines.append(f"- `{name}`")
    lines.extend(
        [
            "",
            "## Execution Behavior",
            "",
            "- `pg_dump --format=custom --no-owner --no-privileges` creates the artifact.",
            "- A JSON manifest is written next to the dump for release evidence.",
            "- CI must use `--dry-run` unless a controlled backup environment is explicitly configured.",
        ]
    )
    return "\n".join(lines) + "\n"


def artifact_paths(output_dir: str, *, timestamp: str | None = None) -> tuple[Path, Path]:
    stamp = timestamp or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = Path(output_dir)
    artifact = base / f"eduboost-postgres-{stamp}.dump"
    return artifact, artifact.with_suffix(".manifest.json")


def build_pg_dump_command(database_url: str, artifact: Path) -> list[str]:
    return [
        "pg_dump",
        "--format=custom",
        "--no-owner",
        "--no-privileges",
        "--file",
        str(artifact),
        database_url,
    ]


def execute_backup(*, output_dir: str, env: dict[str, str] | None = None) -> BackupExecutionResult:
    values = env if env is not None else os.environ
    artifact, manifest = artifact_paths(output_dir)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    command = build_pg_dump_command(values["DATABASE_URL"], artifact)
    subprocess.run(command, check=True)
    manifest.write_text(
        json.dumps(
            {
                "artifact": str(artifact),
                "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tool": "pg_dump",
                "format": "custom",
                "storage_container": values.get("AZURE_STORAGE_CONTAINER", ""),
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return BackupExecutionResult(str(artifact), str(manifest), command)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or preflight an EduBoost database backup.")
    parser.add_argument("--output-dir", default="artifacts/backups", help="Backup artifact output directory.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print backup plan without dumping data.")
    args = parser.parse_args()

    results = validate_environment()
    if not args.dry_run:
        results.append(validate_backup_tool())

    print("Database backup preflight")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: {result.detail}")

    if args.dry_run:
        print(render_plan(args.output_dir, dry_run=True))
        return 0

    if not all(result.ok for result in results):
        return 1

    execution = execute_backup(output_dir=args.output_dir)
    print(f"Backup artifact: {execution.artifact}")
    print(f"Backup manifest: {execution.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
