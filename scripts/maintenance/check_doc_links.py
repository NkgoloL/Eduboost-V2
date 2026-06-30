#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from doc_utils import git_changed_markdown, iter_markdown, relpath

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
MAX_LINK_TARGET_LEN = 2048


def target_exists(path: Path) -> bool:
    try:
        return path.exists()
    except OSError:
        return False


def select_files(root: Path, changed_only: bool) -> list[Path]:
    if changed_only:
        return git_changed_markdown(root)
    return list(iter_markdown(root))


def is_external(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.scheme in {"http", "https", "mailto", "tel"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check local markdown links.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--changed-only", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures: list[str] = []
    files = select_files(root, args.changed_only)

    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            raw = match.group(1).strip()
            if not raw or raw.startswith("#") or is_external(raw):
                continue
            if raw.startswith("file://"):
                failures.append(f"{relpath(path, root)}: local file URI is not allowed: {raw}")
                continue
            target_part = raw.split("#", 1)[0].strip()
            if not target_part:
                continue
            if target_part.startswith("<") and target_part.endswith(">"):
                target_part = target_part[1:-1]
            target_part = unquote(target_part)
            if len(target_part) > MAX_LINK_TARGET_LEN:
                continue
            target = (root / target_part[1:]) if target_part.startswith("/") else (path.parent / target_part)
            if not target_exists(target):
                failures.append(f"{relpath(path, root)}: broken link -> {raw}")

    if failures:
        print("Documentation link check failed:")
        for item in failures[:200]:
            print(f"  - {item}")
        if len(failures) > 200:
            print(f"  ... {len(failures) - 200} more")
        return 1

    print(f"Documentation link check passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
