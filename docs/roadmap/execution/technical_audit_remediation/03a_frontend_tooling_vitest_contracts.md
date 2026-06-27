# TA Phase 03A — Frontend Vitest Contracts

**Status:** implementation-ready  
**Parent slice:** TA Phase 03 — Frontend & Tooling Authority  
**Authority gate:** `python3 scripts/audit_remediation/run_frontend_tooling_authority.py --output-dir docs/release-evidence/technical-audit/frontend-tooling-authority/raw --json`

## Purpose

The first Phase 03 authority run established the frontend/tooling gate but failed on two Vitest contract tests and a frontend evidence-hash control issue.

This slice repairs the high-signal failures without weakening the frontend authority gate.

## Scope

- Align `services.smoke.test.ts` with the canonical POPIA erasure cancel/status proxy paths now used by `DataRightsService`.
- Make `AiTutorChat` safe under jsdom by guarding `scrollIntoView` before invoking it.
- Prevent `frontend_tooling_evidence_check.json` from being included in `SHA256SUMS.txt`, avoiding a self-mutating evidence digest.
- Add focused Phase 03A verification and evidence scripts.

## Boundaries

- No backend-fast evidence is touched.
- No Phase 02R governance is changed.
- No product release-readiness claim is made.
- No Playwright/E2E closure is claimed.
- No runtime KG implementation is introduced.

## Exit criteria

1. `verify_frontend_tooling_phase03a.py --json` returns `valid: true`.
2. Phase 03A focused tests pass.
3. Phase 03A evidence is recorded separately.
4. The full frontend/tooling authority collector is rerun and evidence is committed only if `verify_frontend_tooling_evidence.py` returns `valid: true`.
