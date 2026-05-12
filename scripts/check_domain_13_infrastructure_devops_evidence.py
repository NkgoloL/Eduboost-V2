#!/usr/bin/env python3
"""Verify repo-side evidence for Infrastructure & DevOps roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['bicep', 'k8s', 'docker', 'docker-compose.prod.yml', 'deployment', 'scripts/staging_smoke.py', 'scripts/validate_ops_assets.py', 'scripts/build_release_evidence.py', 'scripts/check_staging_release_gate.py', 'scripts/check_release_evidence_artifacts.py', 'docs/operations', 'docs/release', '.github/workflows/cluster-d-ci.yml', '.github/workflows/release.yml', 'Makefile']
TRACKED_GAPS = ['Dockerfile', 'docs/staging']
EXTERNAL_GATES = ['Green GitHub Actions status must be verified on GitHub after push.', 'Production/staging/cloud evidence cannot be produced from repository files alone.', 'Human owner, legal/privacy, security, curriculum, accessibility, and release approvals cannot be supplied by an agent.', 'Azure resources, Key Vault secrets, staging smoke evidence, backup/restore drills, and image scans require cloud access.']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 13: Infrastructure & DevOps")
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
