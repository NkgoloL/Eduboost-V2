#!/usr/bin/env python3
"""Verify PRD-1.2-1.4 required-check, workflow, and release-gate convergence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.production_readiness.audit_prd102_104_required_checks_workflow_release_gate_convergence import audit


def evaluate(root: Path = Path(".")) -> dict:
    return audit(root)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority-only", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    ok = result.get("authority_valid") if args.authority_only else result.get("valid")
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-1.2-1.4 {'authority_valid' if args.authority_only else 'valid'}: {ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
