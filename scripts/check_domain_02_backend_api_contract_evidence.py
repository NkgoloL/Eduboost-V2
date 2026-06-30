#!/usr/bin/env python3
"""Verify repo-side evidence for Backend API Contract roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['app/domain/api_v2_models.py', 'app/core/exceptions.py', 'app/api_v2.py', 'docs/openapi.json', 'docs/api_envelope_contract.md', 'docs/error_contract.md', 'docs/route_inventory.md', 'scripts/generate_openapi.py', 'scripts/generate_route_inventory.py', '.github/workflows/runtime-contract.yml', '.github/workflows/api-envelope-error-contract.yml']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'Frontend/client consumers must be verified against generated OpenAPI after merge.']
TRACKED_GAPS = []

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 02: Backend API Contract")
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
