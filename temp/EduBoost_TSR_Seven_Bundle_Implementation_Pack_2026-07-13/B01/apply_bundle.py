#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

BUNDLE_ROOT = Path(__file__).resolve().parent
MANIFEST = json.loads((BUNDLE_ROOT / "bundle_manifest.json").read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def locate_repo(value: str) -> Path:
    start = Path(value).resolve()
    for current in (start, *start.parents):
        if all((current / p).exists() for p in ("app", "docs", "scripts", "pyproject.toml")):
            return current
    raise SystemExit(f"ERROR: {start} is not inside an EduBoost repository")


def git_dirty(repo: Path) -> bool:
    if not (repo / ".git").exists():
        return False
    proc = subprocess.run(["git", "status", "--porcelain"], cwd=repo, text=True, capture_output=True, check=False)
    return bool(proc.stdout.strip())


def verify_payload() -> None:
    errors = []
    for rel, expected in MANIFEST["overlay_sha256"].items():
        path = BUNDLE_ROOT / "overlay" / rel
        if not path.exists():
            errors.append(f"missing payload file: {rel}")
        elif sha256(path) != expected:
            errors.append(f"payload digest mismatch: {rel}")
    if errors:
        raise SystemExit("ERROR: bundle payload integrity failed\n" + "\n".join(errors))


def backup_paths(repo: Path, backup: Path) -> None:
    paths = set(MANIFEST.get("mutable_paths", [])) | set(MANIFEST["overlay_sha256"])
    for rel in sorted(paths):
        src = repo / rel
        if src.exists() and src.is_file():
            dst = backup / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        elif src.exists() and src.is_dir():
            dst = backup / rel
            shutil.copytree(src, dst, dirs_exist_ok=True)
    (backup / "_paths.json").write_text(json.dumps(sorted(paths), indent=2) + "\n")


def restore(repo: Path, backup: Path) -> None:
    paths = json.loads((backup / "_paths.json").read_text()) if (backup / "_paths.json").exists() else []
    for rel in sorted(paths, reverse=True):
        target = repo / rel
        saved = backup / rel
        if saved.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(saved, target)
        elif saved.is_dir():
            if target.exists(): shutil.rmtree(target)
            shutil.copytree(saved, target)
        elif target.exists():
            if target.is_dir(): shutil.rmtree(target)
            else: target.unlink()


def install_overlay(repo: Path) -> None:
    for rel in sorted(MANIFEST["overlay_sha256"]):
        src = BUNDLE_ROOT / "overlay" / rel
        dst = repo / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=dst.parent, delete=False) as handle:
            temp = Path(handle.name)
        shutil.copy2(src, temp)
        os.replace(temp, dst)


def run_executor(repo: Path, phase: str, skip_heavy: bool) -> int:
    cmd = [sys.executable, "-m", "scripts.true_state_remediation.execute_bundle", "--repo", str(repo), "--bundle", "B01", "--phase", phase, "--json"]
    if skip_heavy: cmd.append("--skip-heavy")
    proc = subprocess.run(cmd, cwd=repo, check=False)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description=MANIFEST["title"])
    parser.add_argument("--repo", default=".")
    parser.add_argument("--phase", choices=("prepare", "apply", "verify", "all"), default="all")
    parser.add_argument("--skip-heavy", action="store_true", help="Smoke only. This never closes the bundle.")
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--keep-failed-changes", action="store_true")
    args = parser.parse_args()
    repo = locate_repo(args.repo)
    verify_payload()
    if git_dirty(repo) and not args.allow_dirty:
        print("ERROR: worktree is dirty. Commit/stash changes or pass --allow-dirty explicitly.", file=sys.stderr)
        return 2
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = repo / ".tsr" / "backups" / "b01" / stamp
    backup.mkdir(parents=True, exist_ok=True)
    backup_paths(repo, backup)
    try:
        install_overlay(repo)
        rc = run_executor(repo, args.phase, args.skip_heavy)
        if rc != 0:
            raise RuntimeError(f"bundle executor exited {rc}")
        print(f"B01 completed and verified. Backup: {backup}")
        return 0
    except Exception as exc:
        print(f"ERROR: B01 did not close: {exc}", file=sys.stderr)
        print(f"Evidence/failure state is under docs/release-evidence/true-state-remediation/b01", file=sys.stderr)
        if not args.keep_failed_changes:
            restore(repo, backup)
            print(f"Repository files were restored from {backup}", file=sys.stderr)
        else:
            print("Failed changes were retained because --keep-failed-changes was supplied.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
