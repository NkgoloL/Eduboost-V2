# Reviewer Decision Capture Template

## Purpose

The reviewer decision capture template gives the PR reviewer a fixed format to record final merge-review disposition for the controlled staging/beta evidence package.

## Required Reviewer Decision Inputs

- final closure manifest
- branch handoff proof record
- final acceptance memo
- release record closure ledger
- PR merge evidence summary
- final reviewer pack checklist
- merge-control evidence gate
- PR-ready final closure certificate
- final release evidence table of contents
- final evidence no-op execution assertion

## Decision Fields

| Field | Value |
| --- | --- |
| Reviewer Decision ID | pending |
| Release Candidate | pending |
| Commit SHA | pending |
| Branch | pending |
| PR Number | pending |
| Reviewer | pending |
| Decision Time UTC | pending |
| Decision | approve merge / request changes / defer / reject |
| Reason | pending |
| Follow-Up Owner | pending |

## Reviewer Decision Rules

- reviewer decision must reference release candidate and commit SHA
- reviewer decision must reference branch and PR number
- approve merge decision requires merge-control evidence gate review
- request changes decision must identify evidence gap and owner
- defer decision must identify reason and target milestone
- reject decision must identify blocking evidence failure
- reviewer decision must preserve no-op execution boundary
- reviewer decision must not authorize unrestricted production launch

## Boundary

This reviewer decision capture template records reviewer disposition only. It does not approve production launch, execute deployment, create release tags, or merge the pull request automatically.

## Command

```bash
make reviewer-decision-capture-template-check
```

## Reviewer Disposition Terminal Seal PR Handoff Evidence

- `docs/operations/final_reviewer_disposition_record.md`
- `docs/operations/terminal_evidence_seal.md`
- `docs/operations/final_pr_handoff_summary.md`
