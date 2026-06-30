#!/usr/bin/env python3
"""Verify repo-side evidence for Billing & Payments roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['app/api_v2_routers/billing.py', 'docs/adr', 'Makefile']
TRACKED_GAPS = ['app/modules/billing', 'app/services/billing', 'docs/billing_policy.md', 'app/frontend/src/app/billing', 'tests/unit/modules/billing', 'tests/integration/test_billing_webhooks.py', 'scripts/check_billing_evidence.py']
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'Billing provider selection, sandbox credentials, webhook secrets, and payment-provider dashboard validation require human/provider access.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 11: Billing & Payments")
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
