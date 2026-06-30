# TA Phase 04 — CI Authority / Workflow Cleanup

Status: implementation-ready

## Purpose

Close the CI workflow mechanics blocker identified by the technical audit without claiming a remote CI pass.

This slice establishes a static CI workflow authority contract for the repository's main GitHub Actions workflow.

## Scope

In scope:

- Keep `ci-cd.yml` on pnpm for frontend and E2E execution.
- Remove unsupported/stale workflow action pins from the main CI/CD workflow.
- Ensure Playwright is installed and invoked through the repository pnpm contract.
- Ensure production promotion depends on both schema and Alembic drift gates.
- Add a static verifier and evidence collector for CI workflow configuration.

Out of scope:

- Running or claiming remote GitHub Actions success.
- Dependency-scan severity enforcement.
- Runtime KG implementation.
- Product release readiness.

## Authority command

```bash
python3 scripts/audit_remediation/verify_ci_authority_workflow.py --json
```

## Evidence command

```bash
bash scripts/audit_remediation/collect_ci_authority_workflow_evidence.sh
python3 scripts/audit_remediation/verify_ci_authority_workflow_evidence.py \
  --evidence-dir docs/release-evidence/technical-audit/ci-authority-workflow \
  --json
```

## Passing criteria

- Main workflow job ids are unique.
- Frontend and E2E execution use pnpm and `app/frontend/pnpm-lock.yaml`.
- No `npm ci` / `package-lock.json` assumptions remain in `ci-cd.yml`.
- Playwright is invoked via `pnpm exec playwright test`.
- Main workflow artifact uploads use `actions/upload-artifact@v4`.
- Production promotion depends on `schema-drift` and `alembic-drift`.
- Evidence hash manifest excludes its own verifier output.

## Boundary

This phase proves workflow configuration. A later remote-CI evidence slice must attach a real GitHub Actions run URL before claiming hosted CI authority.
