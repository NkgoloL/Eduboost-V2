#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from scripts.testing.targeted_baseline_reconciliation import run_pytest_probe, sanitized_test_environment
from scripts.testing.verify_targeted_baseline_reconciliation import evaluate

TIMEOUT_NODES = (
    "tests/unit/test_envelope_route_background.py::test_enveloped_route_preserves_background_tasks",
    "tests/unit/test_exception_envelopes.py::test_http_exception_uses_canonical_error_envelope",
)
FOCUSED_FILES = (
    "tests/unit/testing/test_targeted_baseline_reconciliation.py",
    "tests/unit/tools/test_mcp_compat.py",
    "tests/unit/test_etl_mcp_server_startup.py",
    "tests/unit/test_envelope_route_background.py",
    "tests/unit/test_exception_envelopes.py",
    "tests/unit/roadmap_reconciliation/test_kg000_formal_kg_roadmap_approval.py",
    "tests/unit/roadmap_reconciliation/test_kg001_caps_graph_foundation.py",
    "tests/unit/roadmap_reconciliation/test_kg002_target_graph_generation.py",
    "tests/unit/roadmap_reconciliation/test_kg003_learner_graph_shadow_mode.py",
    "tests/unit/roadmap_reconciliation/test_prd105_109_ci_convergence_release_readiness_handoff.py",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--require-green", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--timeout-seconds", type=int, default=120)
    args = parser.parse_args()
    root = Path(args.root).resolve()
    verification = evaluate(root)
    plan = {
        "prd_id": "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7",
        "slice": "targeted-baseline-reconciliation",
        "focused_files": list(FOCUSED_FILES),
        "timeout_nodes": list(TIMEOUT_NODES),
        "environment": sanitized_test_environment({}),
        "authority_valid": verification["valid"],
        "executed": args.execute,
    }
    if not args.execute:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if verification["valid"] else 1
    output = root / "var/prd11/runtime-restore/execution-7/targeted-baseline-reconciliation"
    output.mkdir(parents=True, exist_ok=True)
    command = [sys.executable, "-m", "pytest", "-q", *FOCUSED_FILES, "--no-cov"]
    completed = subprocess.run(command, cwd=root, env=sanitized_test_environment(), text=True, capture_output=True, check=False)
    (output / "focused.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (output / "focused.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    probes = [run_pytest_probe(root, node, output / "timeout-probes", timeout_seconds=args.timeout_seconds) for node in TIMEOUT_NODES]
    green = verification["valid"] and completed.returncode == 0 and all(item["green"] for item in probes)
    result = {**plan, "focused_exit_code": completed.returncode, "timeout_probes": probes, "green": green,
              "governance_boundary": {"execution_7_complete_claimed": False, "execution_8_authorised": False, "green_evidence_capture_performed": False}}
    (output / "summary.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"green: {green}")
    if args.require_green and not green:
        return 3
    return 0 if verification["valid"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
