#!/usr/bin/env python3
"""Compatibility wrapper for the Grade 4 Maths launch item bank.

The real generation logic now lives in the registry-driven scope builder.
This wrapper keeps the historical script path working for docs and CI while
delegating artifact creation to the generic scope pipeline.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.curriculum.build_scope_content_artifacts import build_scope_content_artifacts

DEFAULT_SCOPE_ID = "grade4_mathematics_en"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scope-id", default=DEFAULT_SCOPE_ID, help="Registry scope to build.")
    parser.add_argument("--json", action="store_true", help="Emit the build report as JSON.")
    args = parser.parse_args()

    report = build_scope_content_artifacts(args.scope_id, write=True)
    item_total = sum(report["item_counts"].values())
    payload = {
        "scope_id": report["scope_id"],
        "output": report["output_files"]["diagnostic_items"],
        "items": item_total,
        "validation": report["validation"],
    }
    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if not any(report["validation"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
