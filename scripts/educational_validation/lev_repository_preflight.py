#!/usr/bin/env python3
"""Validate baseline repository presence for Longitudinal Educational Validation (LEV)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = [
    "app",
    "docs",
    "scripts",
    "tests",
    "pyproject.toml",
    "docs/roadmap/production_readiness/production_readiness_register.json",
    "app/services/runtime_kg/service.py",
    "app/modules/progress/mastery_model.py",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="LEV repository preflight checks.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    missing = [x for x in REQUIRED if not (root / x).exists()]

    out = {
        "valid": not missing,
        "repo_root": str(root),
        "missing": missing,
        "required": REQUIRED,
    }
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(out)

    raise SystemExit(0 if not missing else 1)


if __name__ == "__main__":
    main()
