#!/usr/bin/env python3
"""Verify Phase 02L backend-fast evidence verifier xfailed handling."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

REQUIRED = [
    "scripts/audit_remediation/verify_backend_fast_evidence.py",
    "tests/unit/audit_remediation/test_backend_fast_phase02l.py",
    "docs/roadmap/execution/technical_audit_remediation/02l_backend_fast_xfailed_evidence_verifier.md",
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

    verifier = root / "scripts/audit_remediation/verify_backend_fast_evidence.py"
    if verifier.exists():
        text = verifier.read_text(encoding="utf-8")
        if "xfailed" not in text:
            errors.append("backend-fast evidence verifier must explicitly document xfailed-safe handling")
        if '"failed," in gate_text' in text or '"failed in" in gate_text' in text:
            errors.append("backend-fast evidence verifier must not use substring failed matching that catches xfailed")
        if "\\s+failed" not in text:
            errors.append("backend-fast evidence verifier must use a word/count based failed-summary regex")
        if r"make: \*\*\* .*Error" not in text:
            errors.append("backend-fast evidence verifier must still reject make error lines")

    register = root / "docs/roadmap/execution/technical_audit_remediation/blocker_register.json"
    if register.exists():
        data = json.loads(register.read_text(encoding="utf-8"))
        if data.get("active_slice") != "02l-backend-fast-xfailed-evidence-verifier":
            errors.append("blocker register active_slice must be 02l-backend-fast-xfailed-evidence-verifier")
        policy = data.get("backend_fast_failure", {}).get("phase_02l_slice", {}).get("policy", "")
        if "xfailed" not in policy:
            errors.append("blocker register must record xfailed-safe evidence policy")
    else:
        errors.append("missing blocker register")

    return {"phase": "02L", "valid": not errors, "errors": errors, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = verify(ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PHASE 02L VERIFIED" if result["valid"] else "PHASE 02L FAILED")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
