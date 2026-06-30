#!/usr/bin/env python3
"""Validate Gate 2R.8 closure readiness without approving Phase 02R closure."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.curriculum.evaluation import build_gate2r8_evaluation_report
from app.services.curriculum.legacy_migration import build_gate2r8_legacy_migration_manifest
from app.services.curriculum.phase02r_closure import evaluate_closure_readiness


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    evaluation = build_gate2r8_evaluation_report()
    legacy = build_gate2r8_legacy_migration_manifest()
    closure = evaluate_closure_readiness(ROOT)
    errors: list[str] = []
    if evaluation.get("status") != "passed":
        errors.append("evaluation report did not pass")
    if legacy.get("status") != "ready_for_review":
        errors.append("legacy migration manifest is not ready for review")
    if closure.status != "ready_for_candidate_closure_evidence":
        errors.extend(closure.failure_reasons or ("closure readiness is blocked",))
    result = {
        "valid": not errors,
        "errors": errors,
        "evaluation_status": evaluation.get("status"),
        "legacy_migration_status": legacy.get("status"),
        "closure_readiness": closure.as_dict(),
        "gate_boundary": {
            "phase_02r_completion_declared": False,
            "production_activation_performed": False,
            "legacy_migration_executed": False,
        },
    }
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["valid"]:
        print("Gate 2R.8 closure-readiness validation passed")
    else:
        print("Gate 2R.8 closure-readiness validation failed", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
