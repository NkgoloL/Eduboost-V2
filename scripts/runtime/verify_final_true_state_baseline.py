"""Verify the PRD-11.0R.RUNTIME-RESTORE-6 final true-state baseline contract."""
from __future__ import annotations

import argparse
import json

from scripts.runtime.final_true_state_baseline import ROOT, collect_final_true_state_baseline, evaluate_final_true_state_handoff_contract


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--run-expensive-checks", action="store_true")
    args = parser.parse_args()
    contract = evaluate_final_true_state_handoff_contract(ROOT)
    baseline = collect_final_true_state_baseline(ROOT, run_expensive_checks=args.run_expensive_checks)
    result = {
        "valid": contract.get("valid") is True and baseline.get("contract_valid") is True,
        "contract": contract,
        "baseline": baseline,
        "all_release_gates_green": baseline.get("all_release_gates_green") is True,
        "next_authorised_item": baseline.get("next_authorised_item"),
    }
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else result)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
