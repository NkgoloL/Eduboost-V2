#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def parse_register(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    current_topic = ""
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if line.startswith("  ") and line.strip().endswith(":") and not line.strip().startswith("-"):
            current_topic = line.strip()[:-1]
        if line.strip().startswith("canonical_path:"):
            value = line.split(":", 1)[1].strip().strip('"\'')
            entries.append((current_topic, value))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate docs/documentation/source_of_truth.yml.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    register = root / "docs/documentation/source_of_truth.yml"
    if not register.exists():
        print("Missing source-of-truth register: docs/documentation/source_of_truth.yml")
        return 1

    entries = parse_register(register)
    if not entries:
        print("No canonical_path entries found in source-of-truth register.")
        return 1

    seen: dict[str, str] = {}
    failures: list[str] = []
    for topic, rel in entries:
        if rel in seen:
            failures.append(f"canonical path reused by {seen[rel]} and {topic}: {rel}")
        seen[rel] = topic
        target = root / rel
        if not target.exists():
            failures.append(f"{topic}: canonical path missing: {rel}")

    if failures:
        print("Source-of-truth register check failed:")
        for item in failures:
            print(f"  - {item}")
        return 1

    print(f"Source-of-truth register check passed for {len(entries)} canonical entries.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
