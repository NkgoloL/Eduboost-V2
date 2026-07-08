"""Verify PRD-2.4-2.6 runtime KG route projection behaviour."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.production_readiness.audit_prd204_206_runtime_kg_route_projection_behaviour import ROOT, audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(Path(ROOT))
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"PRD-2.4-2.6 valid={result['valid']} authority_valid={result['authority_valid']}")


if __name__ == "__main__":
    main()
