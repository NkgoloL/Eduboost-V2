#!/usr/bin/env python3
"""Verify repo-side evidence for Notifications & Communication roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['docs/adr', 'Makefile']
TRACKED_GAPS = ['app/modules/notifications', 'app/services/notifications', 'app/api_v2_routers/notifications.py', 'docs/ops/email_domain_health.md', 'docs/notifications', 'templates/email', 'tests/unit/modules/notifications', 'tests/integration/test_notifications.py', 'scripts/check_notification_evidence.py']
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'Email provider selection, DNS SPF/DKIM/DMARC records, sandbox sends, and legal template review require external access.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 12: Notifications & Communication")
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
