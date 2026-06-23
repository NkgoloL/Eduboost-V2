#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Check documentation-governance workflow consolidation.")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    failures: list[str] = []
    primary = root / ".github/workflows/documentation-governance.yml"
    retired = root / ".github/workflows/documentation-governance-stage2.yml"
    if not primary.exists():
        failures.append("missing consolidated workflow: .github/workflows/documentation-governance.yml")
    else:
        text = primary.read_text(encoding="utf-8", errors="replace")
        required_tokens = [
            "make docs-housekeeping-check",
            "make docs-housekeeping-stage3-check",
            "lfs: false",
            "python-version: \"3.12\"",
        ]
        for token in required_tokens:
            if token not in text:
                failures.append(f"consolidated workflow missing token: {token}")
    if retired.exists():
        failures.append("retired Stage 2 workflow still exists: .github/workflows/documentation-governance-stage2.yml")
    if failures:
        print("Documentation workflow consolidation check failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Documentation workflow consolidation check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
