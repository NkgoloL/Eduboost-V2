# PR Merge Evidence Summary

## Purpose

The PR merge evidence summary gives reviewers a concise merge-facing summary of the final controlled staging/beta evidence state.

## Required Summary Inputs

- final release readiness rollup
- evidence freeze confirmation record
- final reviewer pack checklist
- merge-control evidence gate
- PR-ready final closure certificate
- final release evidence table of contents
- final acceptance packet index
- final evidence no-op execution assertion
- release evidence retention finalization
- post-closeout evidence access policy

## Summary Fields

| Field | Value |
| --- | --- |
| Summary ID | pending |
| Release Candidate | pending |
| Commit SHA | pending |
| Branch | pending |
| PR Number | pending |
| Merge Evidence Outcome | pending |
| Reviewer | pending |
| Reviewed At UTC | pending |
| Follow-Up Owner | pending |

## Merge Summary Rules

- summary must reference release candidate and commit SHA
- summary must reference branch and PR number
- summary must preserve merge-control evidence gate references
- summary must preserve PR-ready final closure certificate references
- summary must preserve final evidence no-op execution assertion
- summary must preserve evidence freeze confirmation record
- summary must preserve controlled staging/beta scope
- summary must not authorize unrestricted production launch

## Boundary

This PR merge evidence summary records reviewer-facing evidence only. It does not approve production launch, execute deployment, create release tags, or merge the pull request automatically.

## Command

```bash
make pr-merge-evidence-summary-check
```

## Acceptance Memo Record Closure Continuity Evidence

- `docs/operations/final_acceptance_memo.md`
- `docs/operations/release_record_closure_ledger.md`
- `docs/operations/post_merge_evidence_continuity_note.md`

## Closure Manifest Branch Handoff Reviewer Decision Evidence

- `docs/operations/final_closure_manifest.md`
- `docs/operations/branch_handoff_proof_record.md`
- `docs/operations/reviewer_decision_capture_template.md`
