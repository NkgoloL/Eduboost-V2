# Terminal Review Index

## Purpose

The terminal review index is the final review map for the sealed controlled staging/beta release evidence package.

## Required Terminal Review Inputs

- final release operator brief
- terminal evidence seal
- final PR handoff summary
- final reviewer disposition record
- reviewer decision capture template
- final closure manifest
- branch handoff proof record
- final acceptance memo
- release record closure ledger
- final release evidence table of contents

## Review Index Order

1. `docs/operations/final_release_operator_brief.md`
2. `docs/operations/terminal_evidence_seal.md`
3. `docs/operations/final_pr_handoff_summary.md`
4. `docs/operations/final_reviewer_disposition_record.md`
5. `docs/operations/reviewer_decision_capture_template.md`
6. `docs/operations/final_closure_manifest.md`
7. `docs/operations/branch_handoff_proof_record.md`
8. `docs/operations/final_acceptance_memo.md`
9. `docs/operations/release_record_closure_ledger.md`
10. `docs/operations/final_release_evidence_toc.md`

## Terminal Review Rules

- terminal review index must reference release candidate and commit SHA
- terminal review index must preserve branch and PR number references
- terminal review index must preserve terminal evidence seal references
- terminal review index must preserve final release operator brief references
- terminal review index must preserve no-op execution boundary references
- terminal review index must remain controlled staging/beta evidence

## Boundary

This terminal review index records reviewer navigation only. It does not approve production launch, execute deployment, create release tags, or merge the pull request automatically.

## Command

```bash
make terminal-review-index-check
```

## Reviewer Closeout Audit Handoff Terminal PR Index Evidence

- `docs/operations/sealed_reviewer_closeout_packet.md`
- `docs/operations/final_audit_handoff_register.md`
- `docs/operations/terminal_pr_evidence_index.md`
