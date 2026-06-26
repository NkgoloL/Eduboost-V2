#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from doc_utils import git_changed_markdown, iter_markdown, load_source_of_truth_paths, relpath, should_relax_metadata

RISKY_PATTERNS = [
    re.compile(r"\bproduction[- ]ready\b", re.I),
    re.compile(r"\brelease[- ]ready\b", re.I),
    re.compile(r"\blaunch approved\b", re.I),
    re.compile(r"\bfully complete\b", re.I),
    re.compile(r"\ball tests pass(?:ed)?\b", re.I),
    re.compile(r"\bgreen baseline\b", re.I),
    re.compile(r"\bPOPIA (?:is )?complete\b", re.I),
    re.compile(r"\bsecurity (?:is )?done\b", re.I),
]

EVIDENCE_HINTS = [
    "evidence_command:",
    "as of ",
    "candidate evidence",
    "not release approval",
    "limited to",
    "known limitations",
    "verification",
    "command",
]


def select_files(root: Path, canonical_only: bool, changed_only: bool) -> list[Path]:
    if canonical_only:
        return [p for p in load_source_of_truth_paths(root) if p.suffix == ".md" and p.exists()]
    if changed_only:
        return git_changed_markdown(root)
    return list(iter_markdown(root))


def has_evidence_nearby(lines: list[str], index: int) -> bool:
    window = "\n".join(lines[max(0, index - 6): min(len(lines), index + 7)]).lower()
    return any(hint in window for hint in EVIDENCE_HINTS)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check broad readiness/security/compliance claims in docs.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--canonical-only", action="store_true")
    parser.add_argument("--changed-only", action="store_true")
    parser.add_argument("--strict-legacy", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    failures: list[str] = []
    files = select_files(root, args.canonical_only, args.changed_only)

    for path in files:
        rel = relpath(path, root)
        if not args.strict_legacy and should_relax_metadata(rel) and not args.canonical_only:
            continue
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for i, line in enumerate(lines):
            for pattern in RISKY_PATTERNS:
                if pattern.search(line) and not has_evidence_nearby(lines, i):
                    failures.append(f"{rel}:{i + 1}: risky claim lacks nearby evidence boundary: {line.strip()[:160]}")

    if failures:
        print("Documentation claim discipline check failed:")
        for item in failures[:200]:
            print(f"  - {item}")
        if len(failures) > 200:
            print(f"  ... {len(failures) - 200} more")
        return 1

    print(f"Documentation claim discipline check passed for {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
