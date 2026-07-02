---
title: "Dependency Pin Report"
status: current-evidence
owner: security
reviewers: [security, engineering, privacy]
audience: security-reviewer
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: 2026-07-02
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage4-check"
code_anchors: [docs/security/README.md, requirements.txt, requirements/base.txt, requirements/dev.txt]
---

# Dependency Pin Report

Generated at: `2026-06-27T02:19:45Z`

**Status:** blocked_unpinned_dependencies

## Blockers

- `requirements.txt:4: arq>=0.25.0`
- `requirements.txt:7: mcp[cli]>=1.0.0`
- `requirements/base.txt:396: mcp[cli]>=1.0.0`
- `requirements/dev.txt:519: mcp[cli]>=1.0.0`
