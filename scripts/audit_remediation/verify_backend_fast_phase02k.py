#!/usr/bin/env python3
"""Verify Phase 02K backend-fast evidence authority repair assets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "scripts/audit_remediation/collect_backend_fast_evidence.sh",
    "scripts/audit_remediation/verify_backend_fast_evidence.py",
    "tests/unit/audit_remediation/test_backend_fast_phase02k.py",
    "docs/roadmap/execution/technical_audit_remediation/02k_backend_fast_evidence_authority.md",
]


def verify(root: Path = ROOT) -> dict[str, object]:
    errors: list[str] = []
    checked: list[str] = []
    for rel in REQUIRED:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required asset: {rel}")
        else:
            checked.append(rel)

    collect = root / "scripts/audit_remediation/collect_backend_fast_evidence.sh"
    if collect.exists():
        text = collect.read_text(encoding="utf-8")
        if "run_json_capture" not in text:
            errors.append("collector must use run_json_capture for machine-readable JSON artifacts")
        if "echo \"$ $*\"" in text:
            errors.append("collector must not prefix candidate JSON evidence with shell command banners")
        if "! -name 'SHA256SUMS.txt'" not in text:
            errors.append("collector must exclude SHA256SUMS.txt from its own hash manifest")
        if "verify_backend_fast_evidence.py" not in text:
            errors.append("collector must run the backend-fast evidence verifier before claiming candidate evidence")

    verifier = root / "scripts/audit_remediation/verify_backend_fast_evidence.py"
    if verifier.exists():
        text = verifier.read_text(encoding="utf-8")
        required_terms = [
            "backend fast gate result must be valid with returncode 0",
            "backend fast failure classification must detect zero failures",
            "backend fast gate output still contains failed/error test lines",
            "must be valid JSON",
            "must not include a self-referential hash",
        ]
        for term in required_terms:
            if term not in text:
                errors.append(f"verifier missing fail-closed check: {term}")

    register = root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    if register.exists():
        data = json.loads(register.read_text(encoding="utf-8"))
        if data.get("active_slice") != "02k-backend-fast-evidence-authority":
            errors.append("blocker register active_slice must be 02k-backend-fast-evidence-authority")
        policy = data.get("backend_fast_failure", {}).get("phase_02k_slice", {}).get("policy", "")
        if "returncode 0" not in policy:
            errors.append("blocker register must record returncode 0 evidence policy")
    else:
        errors.append("missing blocker register")

    return {"phase": "02K", "valid": not errors, "errors": errors, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PHASE 02K VERIFIED" if result["valid"] else "PHASE 02K FAILED")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
