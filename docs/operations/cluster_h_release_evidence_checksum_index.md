# Cluster H Release Evidence Checksum Index

## Purpose

The Cluster H release evidence checksum index defines an integrity-oriented inventory for the final controlled staging/beta release evidence package.

## Required Checksum Subjects

- `docs/operations/cluster_h_terminal_closure_assertion.md`
- `docs/operations/beta_release_final_index.md`
- `docs/operations/beta_governance_seal_checklist.md`
- `docs/operations/final_release_handoff_package.md`
- `docs/operations/evidence_archive_completeness_guard.md`
- `docs/operations/post_terminal_audit_readiness_assertion.md`
- `docs/operations/final_project_closeout_attestation.md`
- `docs/operations/post_beta_evidence_archive_manifest.md`
- `docs/operations/beta_outcome_report_template.md`
- `docs/operations/beta_retrospective_action_register.md`
- `docs/operations/release_owner_execution_guardrail.md`
- `docs/operations/release_audit_trail_index.md`

## Checksum Record Template

| Field | Value |
| --- | --- |
| Evidence Path | pending |
| Release Candidate | pending |
| Commit SHA | pending |
| Hash Algorithm | sha256 |
| Hash Value | pending |
| Recorded By | pending |
| Recorded At UTC | pending |

## Integrity Rules

- checksum index must reference release candidate and commit SHA
- checksum index must use sha256 as the canonical hash algorithm
- checksum index must preserve terminal closure evidence references
- checksum index must preserve handoff and archive evidence references
- checksum index must not include unnecessary learner personal information
- checksum index must remain audit evidence only

## Boundary

This checksum index records evidence integrity expectations. It does not compute hashes automatically, approve production launch, execute deployment, or create release tags.

## Command

```bash
make cluster-h-release-evidence-checksum-index-check
```
