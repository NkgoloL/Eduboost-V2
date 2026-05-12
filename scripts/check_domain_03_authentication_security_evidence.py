#!/usr/bin/env python3
"""Verify repo-side evidence for Authentication & Security roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['app/core/security.py', 'app/core/authorization.py', 'app/core/password_policy.py', 'docs/security/auth_boundary_evidence.md', 'scripts/check_auth_boundary_evidence.py', '.github/workflows/auth-boundary.yml', 'tests/unit/test_auth_boundary_evidence.py']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'Penetration test sign-off and Redis/staging outage behaviour require live environment evidence.']
TRACKED_GAPS = []

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 03: Authentication & Security")
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
