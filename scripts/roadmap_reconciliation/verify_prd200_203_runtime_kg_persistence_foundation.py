"""Verify PRD-2.0-2.3 runtime KG persistence foundation."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.production_readiness.audit_prd200_203_runtime_kg_persistence_foundation import ROOT, audit


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(Path(ROOT))
    if args.authority_only:
        result = {**result, "valid": False}
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-2.0-2.3 valid={result['valid']} authority_valid={result['authority_valid']}")


if __name__ == "__main__":
    main()
