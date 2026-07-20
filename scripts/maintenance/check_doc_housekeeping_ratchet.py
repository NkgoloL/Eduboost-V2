#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from scripts._subprocess import run
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Enforce documentation housekeeping debt ratchets.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--inventory", default="docs/generated/documentation_inventory.json")
    parser.add_argument("--baseline", default="docs/documentation/housekeeping_ratchet_baseline.json")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate deterministic inventory before checking.")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.regenerate:
        rc = run([
            sys.executable,
            "scripts/maintenance/check_doc_inventory_reproducible.py",
            "--root",
            ".",
            "--update",
        ], cwd=root)
        if rc != 0:
            return rc

    inventory_path = root / args.inventory
    baseline_path = root / args.baseline
    if not inventory_path.exists():
        print(f"Missing inventory: {args.inventory}")
        return 1
    if not baseline_path.exists():
        print(f"Missing ratchet baseline: {args.baseline}")
        print("Create it with: python3 scripts/maintenance/update_doc_housekeeping_baseline.py --root .")
        return 1

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    summary = inventory.get("summary", {})
    failures: list[str] = []

    for key, allowed in baseline.get("max_summary", {}).items():
        actual = int(summary.get(key, 0))
        if actual > int(allowed):
            failures.append(f"summary.{key} regressed: actual {actual} > baseline {allowed}")
    for key, minimum in baseline.get("min_summary", {}).items():
        actual = int(summary.get(key, 0))
        if actual < int(minimum):
            failures.append(f"summary.{key} regressed: actual {actual} < baseline {minimum}")

    actual_counts = {str(k): int(v) for k, v in summary.get("finding_counts_by_type", {}).items()}
    max_counts = {str(k): int(v) for k, v in baseline.get("max_findings_by_type", {}).items()}
    for key, actual in sorted(actual_counts.items()):
        if key not in max_counts and baseline.get("strict_zero_new_finding_types", True):
            failures.append(f"new finding type introduced: {key}={actual}")
        elif actual > max_counts.get(key, actual):
            failures.append(f"finding type {key} regressed: actual {actual} > baseline {max_counts.get(key)}")

    if failures:
        print("Documentation housekeeping ratchet failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("Documentation housekeeping ratchet check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
