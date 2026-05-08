#!/usr/bin/env python3
"""
Integrate patch files from a source directory into the repo.

Usage: python3 scripts/integrate_patch.py <source_dir> [--staging-name pr_xxx]

Behavior:
- For each file under <source_dir>, attempt to move it into the repo root preserving relative path.
- If destination already exists, copy the source into `staging/<staging-name>/...` for manual review.
- Stage all moved files and newly created staging files and create a commit summarizing the action.
"""
import os
import sys
import shutil
from pathlib import Path
import subprocess


def run(cmd, cwd=None):
    print(f"> {cmd}")
    subprocess.check_call(cmd, shell=True, cwd=cwd)


def main():
    if len(sys.argv) < 2:
        print("Usage: integrate_patch.py <source_dir> [--staging-name pr_xxx]")
        sys.exit(2)

    src = Path(sys.argv[1])
    staging_name = "pr_009"
    if len(sys.argv) >= 3:
        staging_name = sys.argv[2]

    if not src.exists():
        print(f"Source {src} does not exist")
        sys.exit(1)

    repo_root = Path.cwd()
    staging_root = repo_root / "staging" / staging_name
    staging_root.mkdir(parents=True, exist_ok=True)

    moved = []
    staged_conflicts = []

    for root, dirs, files in os.walk(src):
        rel_root = Path(root).relative_to(src)
        for f in files:
            src_file = Path(root) / f
            dest_file = repo_root / rel_root / f
            dest_dir = dest_file.parent
            if not dest_dir.exists():
                dest_dir.mkdir(parents=True, exist_ok=True)

            if dest_file.exists():
                # conflict -> copy into staging
                target = staging_root / rel_root / f
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, target)
                staged_conflicts.append(target)
                print(f"Conflict: {dest_file} -> staged {target}")
            else:
                # move file into repo
                shutil.move(str(src_file), str(dest_file))
                moved.append(dest_file)
                print(f"Moved: {src_file} -> {dest_file}")

    # clean up empty source dirs
    try:
        for d in sorted(src.glob("**/*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    except Exception:
        pass

    # Stage changes
    try:
        run("git add -A")
        commit_msg = f"chore(integrate): apply patch from {src} (moved {len(moved)} files, staged {len(staged_conflicts)} conflicts)"
        run(f"git commit -m \"{commit_msg}\" || echo 'No changes to commit'")
    except subprocess.CalledProcessError as e:
        print("Git operations failed:", e)
        sys.exit(1)

    print("Integration complete.")
    print(f"Moved files: {len(moved)}")
    print(f"Staged conflicts in: {staging_root}")


if __name__ == '__main__':
    main()
