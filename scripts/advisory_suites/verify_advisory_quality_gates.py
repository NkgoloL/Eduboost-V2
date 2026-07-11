"""Verify PRD-11.0R.RUNTIME-RESTORE-5 advisory quality gate contract."""
from __future__ import annotations

import argparse
import json

from scripts.advisory_suites.advisory_gate import ROOT, evaluate_advisory_quality_gate_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate_advisory_quality_gate_contract(ROOT)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    raise SystemExit(main())
