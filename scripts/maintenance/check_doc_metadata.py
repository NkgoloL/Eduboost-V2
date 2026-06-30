#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from doc_utils import REQUIRED_METADATA_FIELDS, git_changed_markdown, iter_markdown, load_source_of_truth_paths, parse_front_matter, relpath, should_relax_metadata


def select_files(root: Path, canonical_only: bool, changed_only: bool) -> list[Path]:
    if canonical_only:
        return [p for p in load_source_of_truth_paths(root) if p.suffix == ".md" and p.exists()]
    if changed_only:
        changed = git_changed_markdown(root)
        return changed or []
    return list(iter_markdown(root))


def main() -> int:
    parser = argparse.ArgumentParser(description="Check EduBoost documentation metadata front matter.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--canonical-only", action="store_true")
    parser.add_argument("--changed-only", action="store_true")
    parser.add_argument("--strict-legacy", action="store_true", help="Also fail archive/generated/evidence areas.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures: list[str] = []
    files = select_files(root, args.canonical_only, args.changed_only)

    for path in files:
        rel = relpath(path, root)
        if not args.strict_legacy and should_relax_metadata(rel) and not args.canonical_only:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        meta = parse_front_matter(text)
        if not meta:
            failures.append(f"{rel}: missing YAML front matter")
            continue
        missing = [field for field in REQUIRED_METADATA_FIELDS if field not in meta]
        if missing:
            failures.append(f"{rel}: missing metadata fields: {', '.join(missing)}")

    if failures:
        print("Documentation metadata check failed:")
        for item in failures[:200]:
            print(f"  - {item}")
        if len(failures) > 200:
            print(f"  ... {len(failures) - 200} more")
        return 1

    print(f"Documentation metadata check passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
