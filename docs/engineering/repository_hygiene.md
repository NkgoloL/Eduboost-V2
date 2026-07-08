# Repository Hygiene and Generated/Local Artifact Policy

**Owner:** Platform / Engineering  
**Status:** Canonical after PRD-0.9 authority  
**Last updated:** 2026-07-08  
**Control record:** `docs/roadmap/production_readiness/prd_009_repository_hygiene_generated_local_artifact_audit_record.json`

---

## Purpose

PRD-0.9 records the current repository hygiene state after PRD-0.8 branch/release naming reconciliation. It inventories generated, local, cached, backup, command-output, and other non-source artifacts so that later production-readiness work can separate true source authority from local execution residue.

This policy is intentionally conservative: PRD-0.9 is an audit and evidence slice. It does not delete files, rewrite history, rename branches, move release evidence, create release tags, deploy, open public beta traffic, launch billing, or authorise PRD-1 implementation.

---

## Current policy

| Artifact class | Examples | PRD-0.9 disposition |
|---|---|---|
| Runtime logs | `logs/`, `var/`, ad-hoc run logs | Inventory and classify; do not treat as release authority. |
| Test/cache output | `.pytest_cache/`, `.mypy_cache/`, `.ruff_cache/`, `coverage.xml`, `htmlcov/`, `playwright-report/`, `test-results/` | Inventory and keep out of future source-authority claims unless intentionally captured as release evidence. |
| Local temp output | `temp/`, `.tmp/`, `scratch/`, data temp/export folders | Inventory and keep out of source-authority claims. |
| Build/package output | `eduboost.egg-info/`, frontend build outputs, generated Bicep JSON | Inventory and verify canonical source/build authority before later cleanup. |
| Local backups | `.phase*-backup-*`, `.reconciliation-backup-*`, `backups-*` | Inventory; any cleanup must happen in a later explicit remediation slice. |
| Terminal/command-output artifacts | orphaned top-level files produced by shell redirection, pager output, or interrupted commands | Inventory as repository hygiene debt; do not delete in PRD-0.9. |

---

## Authority boundary

PRD-0.9 authorises only the creation of repository hygiene audit records and evidence. It keeps the following gates closed:

- production release;
- deployment;
- release tag creation;
- public beta traffic;
- live learner traffic;
- billing launch;
- live payment processing;
- PRD-1 implementation; and
- any new KG roadmap slice.

The previously authorised runtime KG authority switch remains recorded as already executed. PRD-0.9 does not expand KG implementation scope.

---

## Validation

Run:

```bash
PYTHONPATH=. python3 scripts/roadmap_reconciliation/verify_prd009_repository_hygiene_generated_local_artifact_audit.py --json
```

Before evidence capture the verifier should report `authority_valid: true` and `valid: false`. After evidence capture it should report `authority_valid: true` and `valid: true`, with `next_authorised_item: PRD-0.10`.
