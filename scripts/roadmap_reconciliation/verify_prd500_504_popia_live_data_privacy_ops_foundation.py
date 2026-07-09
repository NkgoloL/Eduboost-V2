"""Verify PRD-5.0-5.4 POPIA live-data privacy operations foundation."""
from __future__ import annotations

import argparse
import json

from scripts.production_readiness.audit_prd500_504_popia_live_data_privacy_ops_foundation import ROOT, audit


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--authority-only", action="store_true")
    args = parser.parse_args()
    result = audit(ROOT)
    if args.authority_only:
        result = {**result, "valid": False}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if (result.get("authority_valid") if args.authority_only else result.get("valid")) else 1


if __name__ == "__main__":
    raise SystemExit(main())
