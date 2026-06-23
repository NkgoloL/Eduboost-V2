---
title: "Boundary Debt Queue"
status: active
owner: architecture
reviewers: [architecture, engineering]
audience: developer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-06-23
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/architecture/README.md]
---

# Boundary Debt Queue

**Status:** active

## Immediate queue

1. Expand router repository-import enforcement beyond POPIA and lessons.
2. Move auth router learner-scope refresh lookup into a canonical AuthService.
3. Resolve duplicate service families by domain:
   - consent
   - audit
   - auth
   - diagnostics
   - lessons
4. Replace legacy `assert_can_access_learner` references with explicit read/write helpers.
5. Enable import-linter in CI once the environment includes `import-linter`.

## Non-goals

- Do not remove active runtime facades without call-site proof.
- Do not delete repositories before canonical service migration.
- Do not suppress boundary violations silently.
