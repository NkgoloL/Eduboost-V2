#!/usr/bin/env python3
"""Verify repo-side evidence for Database & Persistence roadmap branch."""
from __future__ import annotations
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
REQUIRED_EVIDENCE = ['alembic', 'app/repositories', 'scripts/validate_schema_integrity.py', 'scripts/verify_migration_graph.py', 'scripts/check_db_repository_evidence.py', 'scripts/check_database_backup_contract.py', '.github/workflows/migration_check.yml', '.github/workflows/cluster-e-data-resilience.yml']
EXTERNAL_GATES = ['GitHub branch-protection / required-check UI settings require repository-admin access.', 'Green GitHub Actions status must be verified on GitHub after push.', 'Human owner, legal/privacy, security, curriculum, and release approvals cannot be supplied by an agent.', 'Staging backup/restore drills and production migration approvals require live infrastructure.']
TRACKED_GAPS = ['docs/migrations']

def main() -> int:
    missing = [item for item in REQUIRED_EVIDENCE if not (ROOT / item).exists()]
    print("Domain 05: Database & Persistence")
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
