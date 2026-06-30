---
title: Documentation Housekeeping Policy
status: active
owner: documentation-governance
reviewers: [engineering, product, privacy, security, operations, release-management]
audience: developer
source_of_truth: true
supersedes: []
superseded_by: null
last_reviewed: 2026-06-22
review_interval_days: 30
evidence_command: make docs-housekeeping-check
code_anchors: [scripts/maintenance, docs/documentation/source_of_truth.yml]
---

# Documentation Housekeeping Policy

EduBoost documentation must remain smaller, owned, executable, and truthful.

## 1. Required metadata

Every active, policy, generated, or evidence document must start with YAML front matter:

```yaml
title: Human readable title
status: active | generated | evidence | draft | superseded | archived
owner: product | engineering | backend | frontend | architecture | privacy | security | operations | release-management | documentation-governance
reviewers: [role]
audience: developer | operator | reviewer | parent | educator | security | privacy | product
source_of_truth: true | false
supersedes: []
superseded_by: null
last_reviewed: YYYY-MM-DD
review_interval_days: 14 | 30 | 45 | 60 | 90 | 180
evidence_command: make ...
code_anchors: []
```

## 2. Canonical source of truth

`docs/documentation/source_of_truth.yml` decides which document is canonical for each major topic.

Rules:

- A topic gets one canonical path.
- Related documents must link back to the canonical path.
- Superseded documents must be archived or marked `status: superseded`.
- Generated evidence must not replace a human-authored current-state summary.

## 3. Directory model

```text
docs/
  README.md
  current_state.md
  documentation/
  product/
  architecture/
  adr/
  engineering/
  api/
  compliance/
  security/
  operations/
  release/current/
  generated/
  archive/
```

## 4. Generated and evidence material

Generated material belongs in `docs/generated/` or `artifacts/evidence/` unless an existing gate requires a stable path.

Generated files must include either:

- a front matter block with `status: generated`, or
- a sibling manifest describing the generation command.

## 5. Archive policy

Archive instead of delete.

Archived files must have a manifest recording:

- original path
- new path
- reason
- run id
- timestamp
- whether a redirect stub was left behind

## 6. Pull request rules

A PR that changes docs must answer:

- Is this doc canonical, generated, evidence, draft, superseded, or archived?
- Which source-of-truth topic does it belong to?
- Which code path or command proves the claim?
- Does it introduce a readiness claim?
- Does it add or remove local links?

## 7. Enforcement

Use:

```bash
make docs-housekeeping-check
```

The initial adoption mode may check only canonical and changed files while legacy debt is gradually ratcheted down.
