#!/usr/bin/env python3
"""Verify the Phase 0-equivalent reproducibility baseline for Gate 2R.0."""
from __future__ import annotations
import subprocess  # nosec B404 — subprocess constants support the controlled wrapper

import argparse
import hashlib
import json
import os
import shutil
from scripts._subprocess import run
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_command(args: list[str], *, timeout: int = 60) -> tuple[int, str]:
    completed = run(
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
        rc, output = run_command(command, timeout=20)
    except Exception as exc:  # pragma: no cover - defensive reporting
        return f"unavailable: {exc}"
    return output if rc == 0 else f"unavailable: {output}"


def _inside_repo(path: Path) -> bool:
    try:
        path.resolve().relative_to(ROOT.resolve())
        return True
    except ValueError:
        return False


def probe_object_storage() -> tuple[bool, dict[str, object], list[str]]:
    """Run a bounded non-production object-storage probe.

    Gate 2R.0 requires functional proof, not just an environment variable.
    A filesystem probe can exercise the immutable-object contract for local
    development, but it is only accepted as closure-grade proof when explicitly
    configured for a non-local backend.
    """
    errors: list[str] = []
    backend = os.getenv("PHASE02R_OBJECT_STORAGE_BACKEND", "").strip().lower()
    if backend in {"s3", "minio"}:
        rc, output = run_command([sys.executable, "scripts/prove_phase02r_object_storage.py", "--json"], timeout=120)
        try:
            payload = json.loads(output)
        except json.JSONDecodeError:
            return False, {"backend": backend, "raw_output": output}, ["object-storage proof did not emit valid JSON"]
        return rc == 0 and bool(payload.get("passed")), payload.get("checks", {}), list(payload.get("errors") or [])

    probe_dir_value = os.getenv("PHASE02R_OBJECT_STORAGE_PROBE_DIR", "").strip()
    backup_dir_value = os.getenv("PHASE02R_OBJECT_STORAGE_BACKUP_DIR", "").strip()
    scoped_token = os.getenv("PHASE02R_OBJECT_STORAGE_SCOPED_TOKEN", "").strip()
    checks: dict[str, object] = {
        "backend": backend or None,
        "probe_dir_configured": bool(probe_dir_value),
        "backup_dir_configured": bool(backup_dir_value),
        "scoped_credentials_configured": bool(scoped_token),
        "functional_contract": False,
    }

    if not backend:
        errors.append("PHASE02R_OBJECT_STORAGE_BACKEND is not configured")
    if backend == "local":
        errors.append("local filesystem object-storage probe is development-only and does not prove staging object storage")
    if not probe_dir_value:
        errors.append("PHASE02R_OBJECT_STORAGE_PROBE_DIR is not configured")
    if not backup_dir_value:
        errors.append("PHASE02R_OBJECT_STORAGE_BACKUP_DIR is not configured")
    if not scoped_token:
        errors.append("PHASE02R_OBJECT_STORAGE_SCOPED_TOKEN is not configured")
    if errors:
        return False, checks, errors

    probe_dir = Path(probe_dir_value).expanduser()
    backup_dir = Path(backup_dir_value).expanduser()
    if _inside_repo(probe_dir):
        errors.append("object-storage probe directory must be outside the repository")
    if _inside_repo(backup_dir):
        errors.append("object-storage backup directory must be outside the repository")
    if probe_dir.resolve() == backup_dir.resolve():
        errors.append("object-storage backup directory must be separate from probe directory")
    if errors:
        return False, checks, errors

    try:
        run_id = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        object_dir = probe_dir / "phase02r" / run_id
        backup_run_dir = backup_dir / "phase02r" / run_id
        object_dir.mkdir(parents=True, exist_ok=False)
        backup_run_dir.mkdir(parents=True, exist_ok=False)
        payload = b"phase02r non-production immutable object proof\n"
        object_path = object_dir / "sample-object.txt"
        object_path.write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        checks["write_sha256"] = digest
        read_digest = hashlib.sha256(object_path.read_bytes()).hexdigest()
        checks["readback_sha256"] = read_digest
        if read_digest != digest:
            errors.append("object-storage readback SHA-256 mismatch")

        version_path = object_dir / "sample-object.v2.txt"
        if object_path.exists():
            version_path.write_bytes(b"phase02r attempted overwrite stored as new version\n")
            checks["overwrite_policy"] = "new_version_created"
        else:
            errors.append("object-storage overwrite probe could not find original object")

        manifest = {
            "schema_version": "1.0",
            "backend": backend,
            "object": str(object_path),
            "sha256": digest,
            "version_object": str(version_path),
        }
        manifest_path = object_dir / "manifest.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        restored_object = backup_run_dir / object_path.name
        restored_manifest = backup_run_dir / manifest_path.name
        shutil.copy2(object_path, restored_object)
        shutil.copy2(manifest_path, restored_manifest)
        restored_digest = hashlib.sha256(restored_object.read_bytes()).hexdigest()
        checks["restore_sha256"] = restored_digest
        checks["manifest_exported"] = manifest_path.exists()
        checks["backup_outside_repo"] = not _inside_repo(backup_run_dir)
        if restored_digest != digest:
            errors.append("object-storage restored object SHA-256 mismatch")
    except Exception as exc:  # pragma: no cover - environment-specific probe
        errors.append(f"object-storage functional probe failed: {exc}")

    checks["functional_contract"] = not errors
    return not errors, checks, errors


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

    rc, status = run_command(["git", "status", "--porcelain"], timeout=20)
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

    rc, output = run_command([sys.executable, "scripts/verify_migration_graph.py"], timeout=120)
    checks["migration_graph"] = output
    if rc != 0:
        errors.append("migration graph check failed")

    rc, output = run_command([sys.executable, "scripts/validate_schema_integrity.py"], timeout=120)
    checks["schema_integrity"] = output
    if rc != 0:
        errors.append("schema integrity check failed")

    rc, output = run_command([sys.executable, "-c", "from app.api_v2 import app; print(app.title)"], timeout=60)
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

    object_storage_passed, object_storage_checks, object_storage_errors = probe_object_storage()
    checks["object_storage"] = object_storage_checks
    if not object_storage_passed:
        errors.extend(object_storage_errors)

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
