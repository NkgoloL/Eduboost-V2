#!/usr/bin/env python3
"""Verify repo-side evidence for Repository Governance & CI/CD roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['.github/CODEOWNERS', '.github/dependabot.yml', '.github/workflows/openapi-drift.yml', '.github/workflows/migration_check.yml', '.github/workflows/privacy-boundary.yml', '.github/workflows/runtime-contract.yml', '.github/workflows/cluster-d-ci.yml', 'CONTRIBUTING.md', 'docs/repository_governance.md', 'scripts/verify_repo_state.py']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'Issue labels and CODEOWNERS auto-request behaviour require GitHub UI/API verification.']
TRACKED_GAPS = []

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 01: Repository Governance & CI/CD")
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
