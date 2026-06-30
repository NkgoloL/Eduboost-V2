# Release Candidate Evidence Sweep

Date: 2026-05-11
Branch: `codex/pr17-rc-evidence-sweep`
Base: `codex/docs-technical-state-reconciliation`

## Purpose

This sweep records the first clean-worktree release-candidate evidence baseline
after the technical-state reconciliation. It separates checks that are green on
the current branch from checks that still need follow-up PRs before public beta
or production claims.

## Local Green Checks

The following command passed:

```bash
make runtime-check openapi-check route-inventory-check beta-release-readiness-contract-check diagnostics-assessment-check
```

Observed result:

- `app.api_v2:app` imported successfully.
- `app.legacy.api.main:app` imported successfully.
- OpenAPI drift check passed.
- Route inventory drift check passed.
- Beta release readiness contract check passed as documentation-contract
  evidence only.
- Diagnostics assessment check passed, including 12 targeted diagnostics,
  mastery, and practice tests.

The migration/schema portion of this command passed:

```bash
make migration-check
```

Observed result:

- Schema integrity check passed.
- Migration graph check passed with 19 revisions and head `20260510_0200`.

After restoring the hidden legacy 410 compatibility route, the smoke, entrypoint,
and health suite passed:

```bash
python3 -m pytest tests/smoke tests/test_entrypoints.py tests/test_health_checks.py -q --no-cov
```

Observed result:

- 35 passed.
- 4 skipped.

## Follow-Up Required

The combined POPIA command still fails on the clean branch:

```bash
make popia-consent-gate-check
```

Observed result:

- Missing consent markers: 207.
- Baseline allowlist entries: 104.
- New unallowlisted missing markers: 103.
- Stale allowlist entries: 0.

This is intentionally left for the privacy/legal PR in the series. That PR must
decide which findings are acceptable internal helper functions, which need local
consent markers, and which belong in a reviewed allowlist.

## Release Claim

This sweep does not make EduBoost V2 public-beta-ready or production-ready. It
establishes the current clean-branch evidence baseline and identifies POPIA
consent-gate reconciliation as the next high-risk automated blocker.
