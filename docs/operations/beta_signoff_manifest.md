# Beta Sign-Off Manifest

## Metadata

- generated_at_utc: `2026-05-17T22:11:20.812056+00:00`
- branch: `codex/production_readiness`
- commit: `02f3babd855703460eefc1727f5fdc71f44d2a60`
- release_candidate: `unset`

## Required Sign-Off Areas

| Area | Evidence expectation | Sign-off owner | Status |
| --- | --- | --- | --- |
| technical lead sign-off | backend runtime, API, frontend journey, and release gates reviewed | _pending_ | _pending_ |
| privacy/POPIA sign-off | consent, audit, data-rights, and learner privacy boundaries reviewed | _pending_ | _pending_ |
| data resilience sign-off | backup, restore, integrity, and production restore approval boundaries reviewed | _pending_ | _pending_ |
| AI safety sign-off | CAPS alignment, prompt safety, output schemas, refusals, and leakage guards reviewed | _pending_ | _pending_ |
| frontend journey sign-off | learner, parent, denial, accessibility, and Playwright evidence reviewed | _pending_ | _pending_ |
| rollback owner sign-off | rollback procedure, owner, trigger, and communication path reviewed | _pending_ | _pending_ |

## Required Input Evidence

- `docs/operations/beta_release_readiness_contract.md`
- `docs/operations/staging_smoke_evidence_manifest.md`
- `docs/frontend/CLUSTER_G_CLOSURE.md`
- `docs/ai/CLUSTER_F_CLOSURE.md`
- `docs/operations/CLUSTER_E_CLOSURE.md`

## Release Boundary

Beta sign-off is valid only for the referenced commit and release candidate.
Any material code, infrastructure, database, consent, AI safety, or frontend
journey change requires a refreshed sign-off manifest.

## Command

```bash
make beta-signoff-manifest
```
