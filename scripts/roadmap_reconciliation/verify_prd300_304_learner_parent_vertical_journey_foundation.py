"""Verify PRD-3.0-3.4 learner/parent vertical journey foundation."""
from __future__ import annotations

import argparse
import json

from scripts.production_readiness.audit_prd300_304_learner_parent_vertical_journey_foundation import ROOT, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["authority_valid"] and (args.authority_only or result["valid"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
