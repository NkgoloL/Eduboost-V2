#!/usr/bin/env python3
"""Verify repo-side evidence for Legal, Privacy & Documentation roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['docs/data_inventory.md', 'docs/POPIA_COMPLIANCE.md', 'SECURITY.md', 'docs/subprocessor_register.md', 'docs/data_retention_policy.md', 'scripts/check_privacy_legal_release_evidence.py', 'scripts/check_popia_legal_evidence.py', '.github/workflows/cluster-h-release-readiness.yml', 'Makefile']
TRACKED_GAPS = ['docs/privacy_policy.md', 'docs/terms_of_service.md', 'docs/parent_consent_notice.md', 'docs/dpia.md']
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'Legal counsel review, Information Officer registration, DPIA approval, and formal policy approval require human/legal authority.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 14: Legal, Privacy & Documentation")
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
