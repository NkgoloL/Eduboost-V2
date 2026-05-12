#!/usr/bin/env python3
"""Verify repo-side evidence for Diagnostics & Assessment roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['app/modules/diagnostics', 'app/modules/progress', 'app/modules/practice', 'scripts/ci/check_diagnostics_assessment.py', 'scripts/check_learning_evidence.py', 'scripts/check_caps_learning_proof.py', 'docs/caps', 'tests/unit/modules/diagnostics', 'tests/unit/modules/progress', 'tests/unit/modules/practice', '.github/workflows/ci_diagnostics_assessment.yml']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'Psychometric/curriculum review of diagnostics and item bias requires educator/human review.']
TRACKED_GAPS = []

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 07: Diagnostics & Assessment")
    print(f"Repo evidence checked: {len(REQUIRED_EVIDENCE)} item(s)")
    if missing:
        print("Missing repo evidence:")
        for item in missing:
            print(f"- {item}")
        return 1
    print("Repo-side evidence files are present.")
    if TRACKED_GAPS:
        print("Tracked repo gaps from roadmap scope:")
        for item in TRACKED_GAPS:
            print(f"- {item}")
    if EXTERNAL_GATES:
        print("External/human gates remain outside repository verification:")
        for item in EXTERNAL_GATES:
            print(f"- {item}")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
