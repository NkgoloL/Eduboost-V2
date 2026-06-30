#!/usr/bin/env python3
"""Verify repo-side evidence for POPIA, Consent & Compliance roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['docs/security/popia_consent_boundary_matrix.md', 'scripts/popia_sweep.py', 'scripts/check_popia_legal_evidence.py', '.github/workflows/popia-consent-audit.yml', 'docs/POPIA_COMPLIANCE.md', 'docs/data_inventory.md']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'POPIA legal review and guardian-facing notice approval require human legal authority.']
TRACKED_GAPS = ['app/modules/popia', 'app/services/popia', 'docs/security/popia_consent_audit_evidence.md', 'docs/security/popia_legal_evidence.md']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 04: POPIA, Consent & Compliance")
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
