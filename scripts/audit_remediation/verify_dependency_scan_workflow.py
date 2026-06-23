#!/usr/bin/env python3
"""Verify dependency scan workflow uses pnpm names consistently and no broad suppressions."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    path = ROOT / ".github/workflows/dependency-scan.yml"
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if "pnpm-audit:" not in content:
        errors.append("dependency-scan workflow must define pnpm-audit job")
    if "needs.npm-audit" in content:
        errors.append("dependency-scan workflow still references needs.npm-audit")
    if "needs.pnpm-audit.result" not in content:
        errors.append("dependency-scan workflow summary must reference needs.pnpm-audit.result")
    if "|| true" in content:
        errors.append("dependency-scan workflow must not broadly suppress audit failures with || true")
    if "pnpm audit --audit-level=critical" not in content:
        errors.append("dependency-scan workflow must run pnpm audit at the configured critical threshold")

    result = {"valid": not errors, "errors": errors, "checked": str(path.relative_to(ROOT))}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("DEPENDENCY SCAN WORKFLOW PASSED" if not errors else "DEPENDENCY SCAN WORKFLOW FAILED")
        for error in errors:
            print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
