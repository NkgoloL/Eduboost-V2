#!/usr/bin/env python3
"""Verify the Phase 0-equivalent reproducibility baseline for Gate 2R.0."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(args: list[str], *, timeout: int = 60) -> tuple[int, str]:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
    )
    return completed.returncode, completed.stdout.strip()


def version_output(command: list[str]) -> str:
    try:
        rc, output = run(command, timeout=20)
    except Exception as exc:  # pragma: no cover - defensive reporting
        return f"unavailable: {exc}"
    return output if rc == 0 else f"unavailable: {output}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--allow-dirty", action="store_true", help="Report dirty state without failing.")
    args = parser.parse_args()

    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, object] = {}

    checks["python"] = sys.version.split()[0]
    if sys.version_info < (3, 12):
        errors.append("Python 3.12+ is required")

    checks["git"] = version_output(["git", "--version"])
    checks["docker"] = version_output(["docker", "--version"])
    checks["docker_compose"] = version_output(["docker", "compose", "version"])
    checks["node"] = version_output(["node", "--version"])
    checks["pnpm"] = version_output(["pnpm", "--version"])

    for executable in ("git", "docker", "node", "pnpm"):
        if shutil.which(executable) is None:
            errors.append(f"{executable} is not available on PATH")

    rc, status = run(["git", "status", "--porcelain"], timeout=20)
    checks["git_status_porcelain"] = status
    if rc != 0:
        errors.append("git status --porcelain failed")
    elif status and not args.allow_dirty:
        errors.append("worktree is not clean")
    elif status:
        warnings.append("worktree is dirty")

    required_files = [
        "app/frontend/pnpm-lock.yaml",
        "alembic.ini",
        "scripts/verify_migration_graph.py",
        "scripts/validate_schema_integrity.py",
    ]
    for relative in required_files:
        if not (ROOT / relative).exists():
            errors.append(f"required reproducibility file missing: {relative}")
    if not any((ROOT / path).exists() for path in ("requirements.txt", "requirements/base.txt", "requirements/constraints.snapshot.txt")):
        errors.append("required Python dependency lock/input files are missing")

    rc, output = run([sys.executable, "scripts/verify_migration_graph.py"], timeout=120)
    checks["migration_graph"] = output
    if rc != 0:
        errors.append("migration graph check failed")

    rc, output = run([sys.executable, "scripts/validate_schema_integrity.py"], timeout=120)
    checks["schema_integrity"] = output
    if rc != 0:
        errors.append("schema integrity check failed")

    rc, output = run([sys.executable, "-c", "from app.api_v2 import app; print(app.title)"], timeout=60)
    checks["backend_entrypoint"] = output
    if rc != 0:
        errors.append("backend app.api_v2 entrypoint import failed")

    frontend_package = ROOT / "app/frontend/package.json"
    checks["frontend_package_json"] = str(frontend_package.relative_to(ROOT))
    if not frontend_package.exists():
        errors.append("frontend package.json missing")

    secret_names = ["DATABASE_URL", "JWT_SECRET", "ENCRYPTION_KEY"]
    checks["required_env_present"] = {name: bool(os.getenv(name)) for name in secret_names}
    missing_env = [name for name, present in checks["required_env_present"].items() if not present]
    if missing_env:
        warnings.append(f"required runtime env vars are unset for local proof: {', '.join(missing_env)}")

    object_storage_env = [
        "PHASE02R_OBJECT_STORAGE_URL",
        "OBJECT_STORAGE_URL",
        "AZURE_STORAGE_CONNECTION_STRING",
        "S3_ENDPOINT_URL",
        "SUPABASE_URL",
    ]
    checks["object_storage_config_present"] = any(os.getenv(name) for name in object_storage_env)
    if not checks["object_storage_config_present"]:
        errors.append("non-production object-storage configuration is not present")

    checks["redis_available"] = shutil.which("redis-server") is not None or shutil.which("redis-cli") is not None
    if not checks["redis_available"]:
        warnings.append("Redis CLI/server not found on PATH; Docker-backed Redis may still be available in later gates")

    result = {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Phase 0 equivalent baseline")
        for warning in warnings:
            print(f"WARNING: {warning}")
        if errors:
            print("FAIL")
            for error in errors:
                print(f"- {error}")
        else:
            print("PASS")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
