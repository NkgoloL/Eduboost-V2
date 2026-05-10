#!/usr/bin/env python3
"""Database restore command scaffold.

The command defaults to dry-run validation and refuses production targets unless
explicitly allowed.
"""
from __future__ import annotations

import argparse
import os
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


def render_plan(backup_artifact: str, target_environment: str, dry_run: bool) -> str:
    mode = "dry-run" if dry_run else "execute"
    lines = [
        "# Database Restore Plan",
        "",
        f"Mode: `{mode}`",
        f"Backup artifact: `{backup_artifact}`",
        f"Target environment: `{target_environment}`",
        "",
        "## Required Verification",
        "",
        "- verify learner record counts",
        "- verify consent record counts",
        "- verify audit event counts",
        "- run runtime and POPIA consent closure checks",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Run or preflight an EduBoost database restore.")
    parser.add_argument("--backup-artifact", default="artifacts/backups/latest.dump", help="Backup artifact path or ID.")
    parser.add_argument("--target-environment", default="staging", help="Restore target environment.")
    parser.add_argument("--allow-production-target", action="store_true", help="Explicitly allow production restore target.")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print restore plan without mutating data.")
    args = parser.parse_args()

    results = validate_environment()
    results.append(validate_target_environment(args.target_environment, args.allow_production_target))

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

    raise SystemExit("Restore execution is not implemented in this scaffold. Use --dry-run in CI.")


if __name__ == "__main__":
    raise SystemExit(main())
