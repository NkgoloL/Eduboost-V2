#!/usr/bin/env python3
"""Verify TA Phase 02N backend-fast evidence finalization assets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _contains(path: Path, needle: str, errors: list[str]) -> None:
    if not path.exists():
        errors.append(f"missing required asset: {path.relative_to(ROOT)}")
        return
    text = path.read_text(encoding="utf-8")
    if needle not in text:
        errors.append(f"{path.relative_to(ROOT)} must contain {needle!r}")


def verify(root: Path = ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []

    collector = root / "scripts/audit_remediation/collect_backend_fast_evidence.sh"
    verifier = root / "scripts/audit_remediation/verify_backend_fast_evidence.py"
    classifier = root / "scripts/audit_remediation/classify_backend_fast_failures.py"
    doc = root / "docs/roadmap/execution/technical_audit_remediation/02n_backend_fast_evidence_finalization.md"
    tests = root / "tests/unit/audit_remediation/test_backend_fast_phase02n.py"

    for path in (collector, verifier, classifier, doc, tests):
        if path.exists():
            checked.append(str(path.relative_to(root)))
        else:
            errors.append(f"missing required asset: {path.relative_to(root)}")

    _contains(collector, 'rm -rf "$RAW_DIR"', errors)
    _contains(collector, "! -name 'backend_fast_evidence_check.json'", errors)
    _contains(collector, "write_sha256sums", errors)
    _contains(verifier, "backend fast failure classification must report valid=true", errors)
    _contains(verifier, "warnings.append(\"backend fast failure classification recorded diagnostic categories despite zero failures\")", errors)
    _contains(classifier, "categories = _classify_categories(text) if failure_count else {}", errors)
    _contains(doc, "does not change product runtime behaviour", errors)

    return {"valid": not errors, "errors": errors, "warnings": warnings, "checked": checked}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = verify(args.root.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PHASE 02N CHECK PASSED" if result["valid"] else "PHASE 02N CHECK FAILED")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
