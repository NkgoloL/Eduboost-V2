#!/usr/bin/env python3
"""Database backup command scaffold.

This script intentionally defaults to dry-run behavior. It validates the
required production-grade inputs for a future backup executor without dumping
data in CI.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
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
            "## Non-Destructive CI Behavior",
            "",
            "CI must use `--dry-run` unless a controlled backup environment is explicitly configured.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or preflight an EduBoost database backup.")
    parser.add_argument("--output-dir", default="artifacts/backups", help="Backup artifact output directory.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print backup plan without dumping data.")
    args = parser.parse_args()

    results = validate_environment()
    print("Database backup preflight")
    for result in results:
        status = "PASS" if result.ok else "FAIL"
        print(f"- {status} {result.name}: {result.detail}")

    if args.dry_run:
        print(render_plan(args.output_dir, dry_run=True))
        return 0

    if not all(result.ok for result in results):
        return 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    raise SystemExit("Backup execution is not implemented in this scaffold. Use --dry-run in CI.")


if __name__ == "__main__":
    raise SystemExit(main())
