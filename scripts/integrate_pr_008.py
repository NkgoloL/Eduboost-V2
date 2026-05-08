#!/usr/bin/env python3
"""Integrate files from temp_1/code_8 patch into the repository.

Rules:
- If destination path doesn't exist: `git mv` the file/dir into place.
- If destination exists and contents are identical: remove the source from temp (git rm -r).
- If destination exists and differs: move the source into `staging/pr_008/` for manual review.

Run from repo root.
"""
import filecmp
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path.cwd()
SRC = ROOT / "temp_1" / "code_8" / "eduboost_pr_008_devops_observability_dr_patch_files"
STAGING = ROOT / "staging" / "pr_008"


def git(cmd_args):
    return subprocess.check_call(["git"] + cmd_args)


def try_git_mv(src: str, dst: str):
    """Try `git mv`, fallback to filesystem move for untracked sources."""
    try:
        return subprocess.check_call(["git", "mv", src, dst])
    except subprocess.CalledProcessError:
        # fallback: filesystem move and add dst to git (source may be untracked)
        Path(dst).parent.mkdir(parents=True, exist_ok=True)
        shutil.move(src, dst)
        return subprocess.check_call(["git", "add", dst])


def ensure_staging(path: Path):
    target = STAGING / path
    target.parent.mkdir(parents=True, exist_ok=True)
    return target


def handle_path(src_path: Path, rel_path: Path = None):
    if rel_path is None:
        rel_path = src_path.relative_to(SRC)

    dest = ROOT / rel_path

    if not src_path.exists():
        return

    # If destination doesn't exist, safe to move
    if not dest.exists():
        dest_parent = dest.parent
        dest_parent.mkdir(parents=True, exist_ok=True)
        print(f"Moving {src_path} -> {dest}")
        try_git_mv(str(src_path), str(dest))
        return

    # If both are files, compare
    if src_path.is_file() and dest.is_file():
        same = filecmp.cmp(str(src_path), str(dest), shallow=False)
        if same:
            print(f"Source identical to dest; removing {src_path}")
            git(["rm", "-r", str(src_path)])
        else:
            print(f"Conflict (file differs): staging {src_path}")
            target = ensure_staging(rel_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            try_git_mv(str(src_path), str(target))
        return

    # If both are directories, recurse
    if src_path.is_dir() and dest.is_dir():
        for child in sorted(src_path.iterdir()):
            handle_path(child, rel_path / child.name)
        # after processing children, if src_path now empty, remove it
        if not any(src_path.iterdir()):
            try:
                # attempt to remove via git if tracked
                git(["rm", "-r", str(src_path)])
            except Exception:
                shutil.rmtree(src_path, ignore_errors=True)
        return

    # Mixed types or other cases: stage for review
    print(f"Mixed-type or unexpected: staging {src_path}")
    target = ensure_staging(rel_path)
    try_git_mv(str(src_path), str(target))


def main():
    if not SRC.exists():
        print("Source patch directory not found:", SRC)
        return

    STAGING.mkdir(parents=True, exist_ok=True)

    for item in sorted(SRC.iterdir()):
        handle_path(item)

    # Final commit
    try:
        git(["add", "-A"])
        git(["commit", "-m", "chore(pr-008): integrate observability/devops patch files (non-conflicting moved, conflicts staged)"])
    except subprocess.CalledProcessError:
        print("No changes to commit or commit failed.")


if __name__ == "__main__":
    main()
