#!/usr/bin/env python3
"""Verify PRD-0.10 PRD-0 closure evidence and PRD-1 handoff."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from scripts.production_readiness.audit_prd010_prd0_closure_evidence_handoff import audit


def evaluate(root: Path = Path(".")) -> dict[str, Any]:
    return audit(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.10 valid: {result['valid']}")
        print(f"PRD-0.10 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if (result["authority_valid"] if args.authority_only else result["valid"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
