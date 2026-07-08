#!/usr/bin/env python3
"""Apply PRD-0.9 repository hygiene policy.

This script only refreshes the repository hygiene policy document. It does not
remove files, rewrite history, rename branches, create release tags, deploy, or
authorise PRD-1 implementation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

POLICY_DOC = Path("docs/engineering/repository_hygiene.md")
POLICY_DOC_TEXT = '# Repository Hygiene and Generated/Local Artifact Policy\n\n**Owner:** Platform / Engineering  \n**Status:** Canonical after PRD-0.9 authority  \n**Last updated:** 2026-07-08  \n**Control record:** `docs/roadmap/production_readiness/prd_009_repository_hygiene_generated_local_artifact_audit_record.json`\n\n---\n\n## Purpose\n\nPRD-0.9 records the current repository hygiene state after PRD-0.8 branch/release naming reconciliation. It inventories generated, local, cached, backup, command-output, and other non-source artifacts so that later production-readiness work can separate true source authority from local execution residue.\n\nThis policy is intentionally conservative: PRD-0.9 is an audit and evidence slice. It does not delete files, rewrite history, rename branches, move release evidence, create release tags, deploy, open public beta traffic, launch billing, or authorise PRD-1 implementation.\n\n---\n\n## Current policy\n\n| Artifact class | Examples | PRD-0.9 disposition |\n|---|---|---|\n| Runtime logs | `logs/`, `var/`, ad-hoc run logs | Inventory and classify; do not treat as release authority. |\n| Test/cache output | `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `coverage.xml`, `htmlcov/`, `playwright-report/`, `test-results/` | Inventory and keep out of future source-authority claims unless intentionally captured as release evidence. |\n| Local temp output | `temp/`, `.tmp/`, `scratch/`, data temp/export folders | Inventory and keep out of source-authority claims. |\n| Build/package output | `eduboost.egg-info/`, frontend build outputs, generated Bicep JSON | Inventory and verify canonical source/build authority before later cleanup. |\n| Local backups | `.phase*-backup-*`, `.reconciliation-backup-*`, `backups-*` | Inventory; any cleanup must happen in a later explicit remediation slice. |\n| Terminal/command-output artifacts | orphaned top-level files produced by shell redirection, pager output, or interrupted commands | Inventory as repository hygiene debt; do not delete in PRD-0.9. |\n\n---\n\n## Authority boundary\n\nPRD-0.9 authorises only the creation of repository hygiene audit records and evidence. It keeps the following gates closed:\n\n- production release;\n- deployment;\n- release tag creation;\n- public beta traffic;\n- live learner traffic;\n- billing launch;\n- live payment processing;\n- PRD-1 implementation; and\n- any new KG roadmap slice.\n\nThe previously authorised runtime KG authority switch remains recorded as already executed. PRD-0.9 does not expand KG implementation scope.\n\n---\n\n## Validation\n\nRun:\n\n```bash\nPYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd009_repository_hygiene_generated_local_artifact_audit.py --json\n```\n\nBefore evidence capture the verifier should report `authority_valid: true` and `valid: false`. After evidence capture it should report `authority_valid: true` and `valid: true`, with `next_authorised_item: PRD-0.10`.\n'


def apply(root: Path = Path("."), write: bool = False) -> dict:
    path = root / POLICY_DOC
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    changed = current != POLICY_DOC_TEXT
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(POLICY_DOC_TEXT, encoding="utf-8")
    return {
        "repository_hygiene_policy_path": str(POLICY_DOC),
        "changed": changed,
        "repository_hygiene_policy_document_refreshed": True,
        "generated_local_cleanup_authorised": False,
        "file_deletion_authorised": False,
        "repository_history_rewrite_authorised": False,
        "prd1_implementation_authorised": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = apply(Path(args.root), write=args.write)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"PRD-0.9 repository hygiene policy checked. changed={result['changed']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
