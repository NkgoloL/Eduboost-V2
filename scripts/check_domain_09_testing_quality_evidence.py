#!/usr/bin/env python3
"""Verify repo-side evidence for Testing & Quality roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['pytest.ini', 'tests', 'tests/smoke', 'tests/integration', 'tests/e2e', 'scripts/check_frontend_verification_evidence.py', 'scripts/check_ai_refusal_fixtures.py', 'scripts/check_ai_fixture_coverage_matrix.py', '.github/workflows/ci-cd.yml', '.github/workflows/frontend-e2e-opt-in.yml', 'Makefile']
TRACKED_GAPS = ['app/frontend/tests']
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'Coverage gates are only complete when CI publishes coverage artifacts and enforces required checks.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 09: Testing & Quality")
    print(f"Repo evidence checked: {len(REQUIRED_EVIDENCE)} item(s)")
    if missing:
        print("Missing required repo evidence:")
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
