---
title: "Accessibility, PWA, And E2E Evidence"
status: "current-evidence"
owner: "frontend"
reviewers: ["frontend", "product", "privacy"]
audience: "developer"
source_of_truth: false
supersedes: []
superseded_by: null
last_reviewed: "2026-06-24"
review_interval_days: 60
evidence_command: "make docs-housekeeping-stage5-check"
code_anchors: "[app/frontend, docs/frontend/README.md]"
---

# Accessibility, PWA, And E2E Evidence

This index links accessibility contracts, static scan evidence, PWA/offline
assets, and Playwright E2E scaffolding.

Run:

```bash
make accessibility-pwa-e2e-check
```

Verification gaps: real-device mobile checks and Playwright against staging
still require environment evidence.
