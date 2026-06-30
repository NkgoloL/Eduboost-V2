#!/usr/bin/env python3
"""Verify repo-side evidence for Frontend roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['scripts/check_frontend_production_readiness.py', 'docs/frontend/production_frontend_pwa_low_data_contract.md', 'docs/frontend/production_frontend_ux_accessibility_mobile_contract.md', 'docs/frontend/production_learner_parent_ux_contract.md', 'docs/frontend/production_protected_route_guard_contract.md', 'docs/frontend/production_auth_onboarding_ux_contract.md', 'docs/frontend/production_frontend_api_client_contract.md', 'docs/frontend/production_frontend_env_security_contract.md', 'app/frontend/package.json', 'app/frontend/src', 'app/frontend/src/lib', 'app/frontend/src/app', 'docs/frontend', 'scripts/check_frontend_journey_evidence.py', 'scripts/check_frontend_accessibility_contract.py', '.github/workflows/cluster-g-frontend.yml', 'Makefile']
TRACKED_GAPS = ['app/frontend/tests', 'app/frontend/playwright.config.ts', 'docs/frontend_verification_evidence.md']
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'End-to-end frontend acceptance needs a running backend/staging environment and browser CI artifacts.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 08: Frontend")
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
