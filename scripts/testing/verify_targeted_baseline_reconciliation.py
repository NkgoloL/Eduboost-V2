#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.testing.targeted_baseline_reconciliation import (
    TEST_ENVIRONMENT,
    verify_mcp_compatibility,
)


def evaluate(root: Path = Path(".")) -> dict:
    errors: list[str] = []
    conftest = root / "tests/conftest.py"
    text = conftest.read_text(encoding="utf-8") if conftest.exists() else ""
    for key, value in TEST_ENVIRONMENT.items():
        if key in {"APP_ENV", "ENVIRONMENT", "DEBUG"} and f'os.environ["{key}"] = "{value}"' not in text:
            errors.append(f"tests/conftest.py does not force {key}={value}")
    for rel in (
        "scripts/coverage_suites/coverage_baseline_stabilisation.py",
        "scripts/coverage_suites/unit_shard_stabilisation.py",
    ):
        source = (root / rel).read_text(encoding="utf-8")
        if 'env.setdefault("DEBUG", "false")' in source:
            errors.append(f"{rel} still uses setdefault for DEBUG")
        if 'env["DEBUG"] = "false"' not in source:
            errors.append(f"{rel} does not force DEBUG=false")
    mcp = verify_mcp_compatibility(root)
    errors.extend(mcp["errors"])
    for rel in ("requirements/base.in", "requirements/base.txt", "requirements/dev.in", "requirements/dev.txt"):
        path = root / rel
        if path.exists() and "mcp[cli]>=1.9.4" not in path.read_text(encoding="utf-8"):
            errors.append(f"{rel} does not enforce the supported MCP dependency floor")
    report_path = root / "docs/roadmap/production_readiness/targeted_baseline_reconciliation_apply_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8")) if report_path.exists() else {}
    if not report:
        errors.append("targeted baseline reconciliation apply report is missing")
    boundaries = report.get("governance_boundary", {})
    for key in ("execution_7_complete_claimed", "execution_8_authorised", "green_evidence_capture_performed"):
        if boundaries.get(key) is not False:
            errors.append(f"{key} must remain false")
    return {
        "prd_id": "PRD-11.0R.RUNTIME-RESTORE.EXECUTION-7",
        "slice": "targeted-baseline-reconciliation",
        "environment_contract": TEST_ENVIRONMENT,
        "mcp_compatibility_valid": mcp["valid"],
        "apply_report_present": bool(report),
        "governance_boundary_valid": not any("must remain false" in e for e in errors),
        "errors": errors,
        "valid": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = evaluate(Path(args.root))
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"valid: {result['valid']}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
