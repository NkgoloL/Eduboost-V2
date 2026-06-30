# Evidence Attachment Runbook

Generated at: `2026-06-12T17:39:56Z`
Commit: `a70b57616bb29572fcb57961b91a3f68f0c66329`

## Purpose

This runbook tells an operator how to attach real release evidence for CI, external approvals, staging, and live database transaction proof.

It is not evidence by itself.

## Evidence attachment commands

| ID | Category | Purpose | Command | Expected until evidence is attached |
|---|---|---|---|---|
| `CI-001` | `ci` | Attach authoritative GitHub Actions run metadata. | `CI_RUN_URL="https://github.com/NkgoloL/Eduboost-V2/actions/runs/<run_id>" CI_RESULT="passed" CI_WORKFLOW="release" CI_VERIFIED_BY="<name>" make ci-run-evidence-attach` | make ci-run-evidence-release-check fails until accepted CI metadata is recorded |
| `LEGAL-001` | `approval` | Attach POPIA/legal approval metadata. | `APPROVAL_ID="LEGAL-001" APPROVAL_DECISION="approved" APPROVAL_APPROVER="<legal-owner>" APPROVAL_EVIDENCE_URL="https://<approval-record>" APPROVAL_SCOPE="beta release POPIA/legal review" make approval-evidence-attach` | make approval-evidence-release-check fails until all legal/security/content approvals are complete |
| `SEC-001` | `approval` | Attach security approval metadata. | `APPROVAL_ID="SEC-001" APPROVAL_DECISION="approved" APPROVAL_APPROVER="<security-owner>" APPROVAL_EVIDENCE_URL="https://<security-report>" APPROVAL_SCOPE="beta release security review" make approval-evidence-attach` | make approval-evidence-release-check fails until all legal/security/content approvals are complete |
| `CONTENT-001` | `approval` | Attach educator/content approval metadata. | `APPROVAL_ID="CONTENT-001" APPROVAL_DECISION="approved" APPROVAL_APPROVER="<content-owner>" APPROVAL_EVIDENCE_URL="https://<content-signoff>" APPROVAL_SCOPE="beta release content review" make approval-evidence-attach` | make approval-evidence-release-check fails until all legal/security/content approvals are complete |
| `STAGING-001` | `staging` | Attach staging smoke evidence by editing docs/release/staging_smoke_evidence.md and rerunning checks. | `make staging-acceptance-status && make staging-acceptance-local-check` | make staging-acceptance-release-check fails until staging evidence fields contain real accepted metadata |
| `ROUTE-TX-AUTH-001` | `live-db` | Attach auth route live DB rollback evidence. | `TX_SLICE="auth" TX_EVIDENCE_URL="https://<auth-live-db-proof>" TX_TEST_RESULT="passed" TX_DATABASE="postgresql-staging" TX_VERIFIED_BY="<name>" make live-db-tx-evidence-attach` | make live-db-tx-evidence-release-check fails until all route transaction slices have accepted live DB evidence |
| `ROUTE-TX-POPIA-001` | `live-db` | Attach POPIA route live DB rollback evidence. | `TX_SLICE="popia" TX_EVIDENCE_URL="https://<popia-live-db-proof>" TX_TEST_RESULT="passed" TX_DATABASE="postgresql-staging" TX_VERIFIED_BY="<name>" make live-db-tx-evidence-attach` | make live-db-tx-evidence-release-check fails until all route transaction slices have accepted live DB evidence |
| `ROUTE-TX-DIAG-001` | `live-db` | Attach diagnostics route live DB rollback evidence. | `TX_SLICE="diagnostics" TX_EVIDENCE_URL="https://<diagnostics-live-db-proof>" TX_TEST_RESULT="passed" TX_DATABASE="postgresql-staging" TX_VERIFIED_BY="<name>" make live-db-tx-evidence-attach` | make live-db-tx-evidence-release-check fails until all route transaction slices have accepted live DB evidence |

## Staging evidence fields

For `STAGING-001`, update `docs/release/staging_smoke_evidence.md` with real values for:

- `Environment`
- `Staging URL`
- `Commit SHA`
- `GitHub Actions run URL`
- `Smoke command`
- `Smoke result`
- `Health endpoint result`
- `API smoke result`
- `Database migration status`
- `Verified by`
- `Date verified`

Then run:

```bash
make staging-acceptance-status
make staging-acceptance-local-check
make staging-acceptance-release-check
```

## Refresh sequence after attaching evidence

```bash
make ci-run-evidence-status
make approval-evidence-status
make external-approval-status
make staging-acceptance-status
make live-db-tx-evidence-status
make route-tx-slice-rollup
make release-go-no-go-status
make beta-blocker-burndown-plan
make final-gate-refresh
```

## Release-mode sequence

Run these only after real evidence is attached:

```bash
make ci-run-evidence-release-check
make approval-evidence-release-check
make external-approval-release-check
make staging-acceptance-release-check
make live-db-tx-evidence-release-check
make route-tx-slice-rollup-release-check
make beta-blocker-burndown-release-check
make release-go-no-go-release-check
make final-gate-refresh-release-check
```

## No false-closure rules

- Do not replace real GitHub Actions evidence with local pytest or Make output.
- Do not replace legal, security, or content sign-off with generated templates.
- Do not replace staging acceptance with local smoke checks.
- Do not replace live DB rollback proof with route-source scans.
- Do not change the beta decision to GO without release-owner sign-off after all release-mode checks pass.

## Expected current state

Until real CI, staging, approval, and live DB evidence is attached, the correct release posture is `NO-GO`.
