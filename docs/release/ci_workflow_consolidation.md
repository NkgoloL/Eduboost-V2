# EduBoost V2 CI Workflow Consolidation Plan

EduBoost has accumulated many evidence-specific workflows. Those workflows are useful, but the release process needs a small number of primary CI lanes that reviewers can reason about quickly.

## Primary CI lanes

| Lane | Workflow | Purpose |
|---|---|---|
| Core | `.github/workflows/ci-core.yml` | Unit tests, integration tests, route alias policy, release hygiene, OpenAPI drift. |
| Security / Privacy | existing POPIA/authz workflows | Authorization, consent, audit, and secret-leakage evidence. |
| Frontend | existing frontend workflow(s) | Lint, type-check, build, accessibility, and opt-in E2E. |
| Release Evidence | existing cluster/release workflows | Cluster D-H evidence and release package checks. |

## Rule

New release-blocking checks should first be added to a Makefile target. CI workflows should call Makefile targets rather than duplicating shell logic.

## Non-goals

- This change does not delete older workflows.
- This change does not replace POPIA/security evidence workflows.
- This change does not mark staging, legal, security, or beta signoff as complete.

## Required local equivalent

```bash
make ci-core-local
```

## Release evidence

CI evidence must be recorded in:

```text
docs/release/ci_evidence.md
```
