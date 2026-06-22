# Phase 2R Gate 2R.1 Approval Intake Record

**Phase:** 02R
**Gate:** 2R.1
**Approval process status:** Open - evidence refreshed after the current intended implementation source commit
**Implementation source baseline:** `e893cd876e650f4d996876cfedeb203243c5f1e1`
**Refreshed evidence source commit:** `306702b9317cbf6ab57e54041abe6b44ff383caa`
**Refreshed evidence commit:** `622900d9cf5d278edf3984fd1f61c48f952cba7a`
**Gate 2R.1 closure:** Not yet established
**Gate 2R.2 authorisation:** Not yet authorised

## Intake Decision

The Gate 2R.1 approval process may begin because the implementation now has:

- candidate evidence controls;
- safe gate-state validation;
- pending approval records;
- authority-loader row-content verification;
- hardened source download handling;
- archived stale failed evidence;
- stricter future transition validation;
- no current claim that Gate 2R.1 is closed.

## Evidence Freshness Result

Candidate evidence was regenerated after the current implementation source
commit intended for approval. Because the evidence package itself is committed
separately, the machine-verifiable evidence source commit is the clean branch
tip used by the collector, while the implementation baseline remains recorded
separately:

```text
implementation_source_sha = e893cd876e650f4d996876cfedeb203243c5f1e1
source_commit_sha = 306702b9317cbf6ab57e54041abe6b44ff383caa
evidence_commit_sha = 622900d9cf5d278edf3984fd1f61c48f952cba7a
evidence_index_sha256 = 7da390fe366e3fda1afe106931963e6293a3b052edd114a17232db9af0d22d15
remote_branch_sha_at_evidence_handoff = 622900d9cf5d278edf3984fd1f61c48f952cba7a
```

The handoff metadata is recorded in
`docs/release-evidence/atlas/phase-02r/gate-2r1/evidence_handoff_metadata.json`.

## Required Approval Roles

The following review domains must each approve independently:

- Engineering approver - implementation correctness and verifier coverage.
- Rights reviewer - source rights, per-use permissions, and fail-closed policy.
- Curriculum reviewer - Grade 4 Mathematics CAPS source-completeness inventory.
- Evidence custodian - evidence integrity, checksums, metadata, and reproducibility.
- Release manager - gate transition readiness and control-state consistency.

## Explicit Non-Approval Boundary

This intake record does not close Gate 2R.1.
This intake record does not authorise Gate 2R.2.
A separate approval commit is still required after all approvals pass.
