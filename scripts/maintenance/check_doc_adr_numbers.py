#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from doc_utils import write_json_deterministic

ADR_NUMBER_RE = re.compile(r"ADR[-_ ]?(\d{3,})", re.I)


def collect(root: Path) -> dict[str, list[str]]:
    adr_dir = root / "docs/adr"
    numbers: dict[str, list[str]] = defaultdict(list)
    if not adr_dir.exists():
        return {}
    for path in sorted(adr_dir.glob("*.md"), key=lambda p: p.as_posix()):
        match = ADR_NUMBER_RE.search(path.name)
        if match:
            numbers[match.group(1)].append(path.relative_to(root).as_posix())
    return {num: paths for num, paths in sorted(numbers.items()) if len(paths) > 1}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check duplicate ADR numbers with a ratcheted baseline.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--baseline", default="docs/documentation/adr_number_baseline.json")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--strict", action="store_true", help="Require zero duplicate ADR numbers.")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    duplicates = collect(root)
    baseline_path = root / args.baseline

    if args.update:
        payload = {
            "schema_version": "doc-adr-number-baseline/v1",
            "note": "Known duplicate ADR numbers captured as a Stage 2 ratchet baseline. Do not add new duplicates.",
            "duplicate_adr_numbers": duplicates,
        }
        write_json_deterministic(baseline_path, payload)
        print(f"Updated {args.baseline}")
        return 0

    if args.strict and duplicates:
        print("Duplicate ADR numbers found:")
        for number, paths in duplicates.items():
            print(f"  - ADR-{number}: {', '.join(paths)}")
        return 1

    if not baseline_path.exists():
        print(f"Missing ADR baseline: {args.baseline}")
        print("Create it with: python3 scripts/maintenance/check_doc_adr_numbers.py --root . --update")
        return 1

    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    allowed = baseline.get("duplicate_adr_numbers", {})
    failures: list[str] = []
    for number, paths in duplicates.items():
        if number not in allowed:
            failures.append(f"new duplicate ADR number ADR-{number}: {', '.join(paths)}")
        elif sorted(paths) != sorted(allowed[number]):
            failures.append(f"ADR-{number} duplicate set changed; resolve or refresh baseline intentionally")
    for number in allowed:
        if number not in duplicates:
            # This is a good change, but the baseline must be refreshed so improvements are kept.
            failures.append(f"ADR-{number} duplicate appears resolved; refresh baseline to lock in improvement")

    if failures:
        print("ADR number ratchet failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("ADR number ratchet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
