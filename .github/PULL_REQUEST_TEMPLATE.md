---
title: ".Github — Pull Request Template"
status: "active"
owner: "engineering"
reviewers: ['engineering', 'architecture']
audience: "internal"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-09-13"
review_interval_days: 90
evidence_command: "make docs-housekeeping-check"
code_anchors: "[]"
---
## Summary

What does this PR change?

## Type of change

- [ ] Bug fix
- [ ] Feature
- [ ] Refactor
- [ ] Documentation
- [ ] Infrastructure

## Testing

- [ ] Unit tests added or updated
- [ ] Full local tests pass
- [ ] Evidence attached in `docs/release/`

## POPIA impact

Does this PR touch learner data, consent, audit, PII, or LLM prompts?

- [ ] No
- [ ] Yes — describe impact:

## Database migrations

- [ ] No migration
- [ ] Migration included with rollback plan

## Security impact

- [ ] No auth/authz/secrets impact
- [ ] Auth/authz/secrets impact reviewed

## Deployment notes

Environment variables or operational changes:

## Release evidence

- [ ] TODO IDs addressed:
- [ ] Evidence files updated under `docs/release/`:
- [ ] Validation commands run:

## Rollback plan

- [ ] No rollback impact
- [ ] Rollback covered by `docs/release/rollback_runbook.md`
- [ ] Database rollback or restore path documented

## Reviewer focus

Call out the highest-risk areas reviewers should inspect:
