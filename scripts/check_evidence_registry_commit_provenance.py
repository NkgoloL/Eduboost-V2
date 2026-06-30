#!/usr/bin/env python3
from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from scripts.evidence_registry import PROVEN_STATUSES, load_registry, validate_registry  # noqa: E402

CRITICAL = [
    "scripts/evidence_registry.py",
    "scripts/stamp_evidence_registry_commit.py",
    "scripts/check_evidence_registry_commit_provenance.py",
    "tests/unit/test_evidence_registry_commit_provenance.py",
]


def main() -> int:
    failures: list[str] = []
    print("Evidence registry commit provenance check")
    findings = load_registry(ROOT / "docs/release/evidence_status_registry.yml")
    errors = validate_registry(findings, ROOT)
    if errors:
        failures.extend(errors)
        for error in errors:
            print(f"- FAIL {error}")
    else:
        print("- PASS registry validation")

    for finding in findings:
        if finding.proof_status in PROVEN_STATUSES:
            if finding.last_verified_commit:
                print(f"- PASS {finding.id} has last_verified_commit={finding.last_verified_commit}")
            else:
                failures.append(f"{finding.id} missing last_verified_commit")

    for path in CRITICAL:
        ast.parse((ROOT / path).read_text(encoding="utf-8"))
        print(f"- PASS syntax {path}")

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-c",
            "pytest.ini",
            "tests/unit/test_evidence_registry_commit_provenance.py",
            "-q",
            "--no-cov",
            "--tb=short",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env={"PYTHONPATH": str(ROOT), **__import__("os").environ},
        check=False,
    )
    print(result.stdout)
    if result.returncode != 0:
        failures.append("evidence registry commit provenance tests failed")

    if failures:
        print("Failures:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("- PASS evidence registry commit provenance check")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
