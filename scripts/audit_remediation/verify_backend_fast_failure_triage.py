#!/usr/bin/env python3
"""Verify Technical Audit Phase 02A backend fast failure-triage controls."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SCRIPTS = [
    "scripts/audit_remediation/verify_backend_fast_environment.py",
    "scripts/audit_remediation/backend_fast_failure_report.py",
    "scripts/audit_remediation/import_backend_fast_failed_evidence.sh",
    "scripts/audit_remediation/run_backend_fast_category_probe.py",
]


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _latest_failure_evidence(root: Path) -> Path | None:
    base = root / "docs/release-evidence/technical-audit/backend-fast-gate-failure"
    if not base.exists():
        return None
    candidates = sorted(path for path in base.iterdir() if path.is_dir())
    return candidates[-1] if candidates else None


def verify(root: Path = ROOT, *, require_failure_evidence: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    doc_path = root / "docs/roadmap/execution/technical_audit_remediation/02a_backend_fast_failure_triage.md"
    if not doc_path.exists():
        errors.append("missing Phase 02A backend fast failure-triage doc")
    else:
        checked.append(str(doc_path.relative_to(root)))
        text = doc_path.read_text(encoding="utf-8")
        if "Failed authority gate captured" not in text:
            errors.append("Phase 02A doc must distinguish failed diagnostic evidence from passing evidence")
        if "runtime knowledge-graph" not in text.lower():
            warnings.append("Phase 02A doc should preserve the KG runtime non-scope boundary")

    for rel_path in REQUIRED_SCRIPTS:
        if not (root / rel_path).exists():
            errors.append(f"missing required script: {rel_path}")
        else:
            checked.append(rel_path)

    register_path = root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    if not register_path.exists():
        errors.append("missing blocker_register.json")
    else:
        checked.append(str(register_path.relative_to(root)))
        register = _load_json(register_path)
        if register.get("active_slice") != "02a-backend-fast-failure-triage":
            errors.append("blocker register active_slice must be 02a-backend-fast-failure-triage")
        blockers = register.get("remaining_release_blockers_after_reset", [])
        backend = [item for item in blockers if isinstance(item, dict) and item.get("id") == "TA-BACKEND-FAST-001"]
        if not backend:
            errors.append("blocker register must track TA-BACKEND-FAST-001")
        else:
            status = backend[0].get("status")
            if status != "blocked_failed_authority_gate":
                errors.append("TA-BACKEND-FAST-001 must be blocked_failed_authority_gate")
        failure = register.get("backend_fast_failure", {})
        if failure.get("passing_evidence_policy") is None:
            errors.append("blocker register must record passing evidence policy for failed backend gate")

    latest = _latest_failure_evidence(root)
    if latest is None:
        if require_failure_evidence:
            errors.append("no imported failed backend-fast diagnostic evidence found")
        else:
            warnings.append("no imported failed backend-fast diagnostic evidence found yet")
    else:
        checked.append(str(latest.relative_to(root)))
        index = latest / "evidence_index.md"
        report = latest / "raw/backend_fast_failure_report.json"
        if not index.exists():
            errors.append(f"missing failed evidence index: {index}")
        else:
            index_text = index.read_text(encoding="utf-8")
            if "Status:** Failed authority gate captured — remediation pending" not in index_text:
                errors.append("failed evidence index must use non-passing status wording")
            if "Candidate verification passed" in index_text:
                errors.append("failed evidence index must not claim candidate verification passing")
            if not re.search(r"Source commit:\*\*\s*[0-9a-f]{40}", index_text):
                errors.append("failed evidence index should include a 40-character source commit")
        if not report.exists():
            errors.append(f"missing failed evidence report: {report}")
        else:
            payload = _load_json(report)
            if payload.get("valid") is True:
                errors.append("failed evidence report unexpectedly reports valid=true")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--require-failure-evidence", action="store_true")
    args = parser.parse_args()
    result = verify(args.root.resolve(), require_failure_evidence=args.require_failure_evidence)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("BACKEND FAST FAILURE TRIAGE PASSED" if result["valid"] else "BACKEND FAST FAILURE TRIAGE FAILED")
        for error in result["errors"]:
            print(f"- {error}")
        for warning in result["warnings"]:
            print(f"warning: {warning}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
