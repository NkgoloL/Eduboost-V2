#!/usr/bin/env python3
"""Verify PRD-0.9 repository hygiene and generated/local artifact audit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.production_readiness.audit_prd009_repository_hygiene_generated_local_artifact_audit import audit


def evaluate(root: Path = Path(".")) -> dict:
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
        print(f"PRD-0.9 valid: {result['valid']}")
        print(f"PRD-0.9 authority_valid: {result['authority_valid']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
        for warning in result["warnings"]:
            print(f"WARNING: {warning}")
    return 0 if (result["authority_valid"] if args.authority_only else result["valid"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
